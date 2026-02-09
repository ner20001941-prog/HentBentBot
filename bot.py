#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import logging
from datetime import datetime
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

# Проверка для Railway
IS_RAILWAY = os.environ.get('RAILWAY_ENVIRONMENT') is not None
PORT = int(os.environ.get('PORT', 8000))

# Импорты python-telegram-bot
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    PreCheckoutQueryHandler,
    MessageHandler,
    Filters,
    CallbackContext
)

# Импортируем наши модули
try:
    from config import BOT_TOKEN, TARIFFS, ADMIN_ID, CHANNEL_LINK, CHANNEL_ID, PORT
    import database as db
    import keyboards as kb
    print("✅ Конфигурация загружена")
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    sys.exit(1)

# Настройка логгирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger.getLogger(__name__)

print("=" * 60)
print("🤖 БОТ ПРОДАЖИ ДОСТУПА К КАНАЛУ ЗА ЗВЁЗДЫ")
print("=" * 60)
print(f"Токен: {BOT_TOKEN[:10]}...")
print(f"Админ: {ADMIN_ID}")
print(f"Канал: {CHANNEL_LINK}")
print(f"Режим: {'🚂 RAILWAY' if IS_RAILWAY else '💻 ЛОКАЛЬНО'}")
print(f"Порт: {PORT}")
print("=" * 60)


# Health check сервер для Railway
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health' or self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {
                "status": "ok",
                "service": "telegram-bot",
                "bot": "running",
                "timestamp": datetime.now().isoformat(),
                "users_count": db.get_stats()["total_users"]
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Отключаем стандартное логирование запросов
        pass


def start_health_server():
    """Запуск health check сервера"""
    server = HTTPServer(('0.0.0.0', PORT), HealthHandler)
    logger.info(f"🌐 Health server запущен на порту {PORT}")
    server.serve_forever()


# ========== ОСНОВНЫЕ КОМАНДЫ ==========

def start_command(update: Update, context: CallbackContext):
    """Команда /start - главное меню"""
    user = update.effective_user
    user_id = user.id

    # Регистрируем пользователя в базе
    db.register_user(user_id, user.first_name, user.username)

    # Проверяем доступ
    has_access = db.has_channel_access(user_id)

    welcome_text = f"""
👋 <b>Привет, {user.first_name}!</b>

🌟 <b>Доступ к эксклюзивному каналу за Telegram Stars</b>

Канал: {CHANNEL_LINK}

{'✅ <b>У вас есть доступ к каналу!</b>' if has_access else '❌ <b>Доступа пока нет</b>'}
"""

    update.message.reply_text(
        welcome_text,
        reply_markup=kb.get_main_menu(has_access),
        parse_mode="HTML",
        disable_web_page_preview=True
    )


def help_command(update: Update, context: CallbackContext):
    """Команда /help"""
    help_text = """
<b>🌟 Как купить доступ к каналу?</b>

1. <b>Выберите тариф</b> - нажмите "Купить доступ за звёзды"
2. <b>Оплатите Stars</b> - внутри Telegram
3. <b>Получите ссылку</b> - сразу после оплаты

<b>💎 Что такое Telegram Stars?</b>
Это внутренняя валюта Telegram для покупки товаров и услуг.
Пополнить звёзды можно через @PremiumBot

<b>🔗 После оплаты:</b>
В меню появится кнопка "Получить ссылку на канал"
"""

    update.message.reply_text(help_text, parse_mode="HTML")


# ========== ОБРАБОТКА КНОПОК ==========

def button_handler(update: Update, context: CallbackContext):
    """Обработчик всех кнопок"""
    query = update.callback_query
    query.answer()

    user_id = update.effective_user.id
    data = query.data

    # КНОПКА НАЗАД
    if data == "back_to_main":
        has_access = db.has_channel_access(user_id)
        welcome_text = f"""
👋 <b>Главное меню</b>

Канал: {CHANNEL_LINK}

{'✅ У вас есть доступ к каналу!' if has_access else '💎 Купите доступ за звёзды'}
"""
        query.edit_message_text(
            text=welcome_text,
            reply_markup=kb.get_main_menu(has_access),
            parse_mode="HTML",
            disable_web_page_preview=True
        )

    # КНОПКА КУПИТЬ ДОСТУП
    elif data == "buy_access":
        tariffs_text = "<b>💎 Выберите тариф:</b>\n\n"

        for tariff_id, tariff in TARIFFS.items():
            duration = "навсегда" if not tariff.get("days") else f"{tariff['days']} дней"
            tariffs_text += f"<b>{tariff['name']}</b>\n💰 {tariff['price']} ⭐ | 📅 {duration}\n{tariff['description']}\n\n"

        query.edit_message_text(
            text=tariffs_text,
            reply_markup=kb.get_tariffs_keyboard(),
            parse_mode="HTML"
        )

    # КНОПКА ВЫБОРА ТАРИФА
    elif data.startswith("buy_"):
        tariff_id = data.replace("buy_", "")
        tariff = TARIFFS.get(tariff_id)

        if not tariff:
            query.answer("❌ Тариф не найден", show_alert=True)
            return

        # Для Telegram Stars используем специальную валюту XTR
        currency = "XTR"  # Код валюты для Telegram Stars

        # Отправляем счет для оплаты
        try:
            context.bot.send_invoice(
                chat_id=query.message.chat_id,
                title=tariff["name"],
                description=tariff["description"],
                payload=f"tariff_{tariff_id}_{user_id}",
                provider_token=None,  # Для Telegram Stars provider_token не нужен
                currency=currency,
                prices=[LabeledPrice(label=tariff["name"], amount=tariff["price"])],
                start_parameter=tariff_id,
                need_name=False,
                need_phone_number=False,
                need_email=False,
                need_shipping_address=False,
                is_flexible=False,
                disable_notification=False
            )
        except Exception as e:
            logger.error(f"Ошибка отправки инвойса: {e}")
            query.answer("❌ Ошибка создания платежа", show_alert=True)

    # КНОПКА ПОЛУЧИТЬ ССЫЛКУ
    elif data == "get_channel_link":
        if db.has_channel_access(user_id):
            query.edit_message_text(
                text=f"<b>🔗 Ваша ссылка на канал:</b>\n\n{CHANNEL_LINK}\n\nНажмите на ссылку выше для входа.",
                parse_mode="HTML",
                disable_web_page_preview=False
            )
        else:
            query.answer("❌ У вас нет доступа! Купите подписку.", show_alert=True)

    # КНОПКА МОЙ ДОСТУП
    elif data == "my_access":
        access_info = db.get_user_access_info(user_id)

        if access_info:
            expires_at = access_info.get("expires_at")
            tariff_name = access_info.get("tariff_name", "Неизвестный тариф")

            if expires_at and expires_at != "forever":
                try:
                    expiry_date = datetime.fromisoformat(expires_at)
                    days_left = (expiry_date - datetime.now()).days
                    if days_left > 0:
                        status_text = f"✅ Активен (осталось {days_left} дней)"
                    else:
                        status_text = "❌ Доступ истек"
                except:
                    status_text = "✅ Доступ активен"
            else:
                status_text = "✅ Бессрочный доступ"

            text = f"""
<b>📊 Ваш доступ:</b>

Тариф: {tariff_name}
Статус: {status_text}
Дата покупки: {access_info.get('granted_at', 'Неизвестно')}

<b>Канал:</b> {CHANNEL_LINK}
"""
        else:
            text = f"""
❌ <b>У вас нет активного доступа</b>

Купите подписку, чтобы получить доступ к каналу:
{CHANNEL_LINK}
"""

        query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💎 Купить доступ", callback_data="buy_access")],
                [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]
            ]),
            parse_mode="HTML",
            disable_web_page_preview=True
        )

    # КНОПКА ПОМОЩЬ
    elif data == "help":
        help_text = """
<b>🌟 Как купить доступ к каналу?</b>

1. <b>Выберите тариф</b> - нажмите "Купить доступ за звёзды"
2. <b>Оплатите Stars</b> - внутри Telegram
3. <b>Получите ссылку</b> - сразу после оплаты

<b>💎 Что такое Telegram Stars?</b>
Это внутренняя валюта Telegram для покупки товаров и услуг.
Пополнить звёзды можно через @PremiumBot
"""
        query.edit_message_text(
            text=help_text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💎 Купить доступ", callback_data="buy_access")],
                [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]
            ]),
            parse_mode="HTML"
        )

    # КНОПКА ПРЕДПРОСМОТР
    elif data == "preview":
        query.edit_message_text(
            text=f"<b>👁️ Предпросмотр канала</b>\n\nКанал: {CHANNEL_LINK}\n\nДля доступа к приватному контенту приобретите подписку!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💎 Купить доступ", callback_data="buy_access")],
                [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]
            ]),
            parse_mode="HTML",
            disable_web_page_preview=True
        )


# ========== ОБРАБОТКА ОПЛАТЫ ==========

def precheckout_handler(update: Update, context: CallbackContext):
    """Подтверждение оплаты"""
    query = update.pre_checkout_query

    try:
        # Проверяем, что это наш товар
        if query.invoice_payload.startswith("tariff_"):
            query.answer(ok=True)
        else:
            query.answer(ok=False, error_message="Неизвестный товар")
    except Exception as e:
        logger.error(f"Ошибка в precheckout: {e}")
        query.answer(ok=False, error_message="Произошла ошибка")


def successful_payment_handler(update: Update, context: CallbackContext):
    """Успешная оплата - выдаём доступ"""
    payment = update.message.successful_payment
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name

    logger.info(f"Получен платеж от {user_id}: {payment.total_amount} {payment.currency}")

    try:
        # Получаем ID тарифа из payload
        if payment.invoice_payload.startswith("tariff_"):
            parts = payment.invoice_payload.split("_")
            if len(parts) >= 2:
                tariff_id = parts[1]
                tariff = TARIFFS.get(tariff_id)

                if tariff:
                    # Добавляем доступ в базу
                    db.add_channel_access(user_id, tariff_id)

                    # Отправляем подтверждение и ссылку
                    success_text = f"""
<b>✅ Оплата прошла успешно!</b>

Спасибо за покупку! Вы приобрели:
<b>{tariff['name']}</b>

<b>🔗 Ссылка на канал:</b>
{CHANNEL_LINK}

Нажмите на ссылку выше для входа в канал.
"""
                    update.message.reply_text(
                        success_text,
                        parse_mode="HTML",
                        disable_web_page_preview=False,
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton("🔗 Открыть канал", url=CHANNEL_LINK)],
                            [InlineKeyboardButton("📊 Мой доступ", callback_data="my_access")],
                            [InlineKeyboardButton("💎 Купить ещё", callback_data="buy_access")]
                        ])
                    )

                    # Уведомление админу
                    try:
                        context.bot.send_message(
                            ADMIN_ID,
                            f"💰 <b>Новая продажа!</b>\n\n"
                            f"👤 Пользователь: {user_name} (ID: {user_id})\n"
                            f"📦 Тариф: {tariff['name']}\n"
                            f"💎 Сумма: {payment.total_amount} звезд\n"
                            f"🆔 Payload: {payment.invoice_payload}",
                            parse_mode="HTML"
                        )
                    except Exception as e:
                        logger.error(f"Ошибка отправки уведомления админу: {e}")

                    # Пытаемся добавить пользователя в канал
                    if CHANNEL_ID:
                        try:
                            context.bot.approve_chat_join_request(
                                chat_id=CHANNEL_ID,
                                user_id=user_id
                            )
                        except Exception as e:
                            logger.error(f"Ошибка при добавлении в канал: {e}")
                else:
                    update.message.reply_text("❌ Ошибка: тариф не найден")
    except Exception as e:
        logger.error(f"Ошибка обработки платежа: {e}")
        update.message.reply_text("❌ Произошла ошибка при обработке платежа")


# ========== АДМИН КОМАНДЫ ==========

def admin_stats_command(update: Update, context: CallbackContext):
    """Статистика для админа /stats"""
    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("❌ Только для администратора")
        return

    stats = db.get_stats()

    stats_text = f"""
<b>📊 Статистика бота:</b>

👥 Всего пользователей: {stats['total_users']}
✅ С активным доступом: {stats['active_users']}
💰 Всего продаж: {stats['total_sales']}
💎 Общая выручка: {stats['total_revenue']} ⭐

<b>Канал:</b> {CHANNEL_LINK}
<b>Режим:</b> {'🚂 Railway' if IS_RAILWAY else '💻 Локально'}
"""

    update.message.reply_text(stats_text, parse_mode="HTML")


def broadcast_command(update: Update, context: CallbackContext):
    """Рассылка сообщения всем пользователям /broadcast"""
    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("❌ Только для администратора")
        return

    if not context.args:
        update.message.reply_text("Использование: /broadcast <текст сообщения>")
        return

    message = ' '.join(context.args)
    users = db.get_all_users()

    success = 0
    failed = 0

    for user_id in users:
        try:
            context.bot.send_message(user_id, f"📢 <b>Рассылка от администратора:</b>\n\n{message}", parse_mode="HTML")
            success += 1
        except Exception as e:
            failed += 1
            logger.error(f"Ошибка отправки пользователю {user_id}: {e}")

    update.message.reply_text(f"✅ Рассылка завершена:\nУспешно: {success}\nНе удалось: {failed}")


def test_access_command(update: Update, context: CallbackContext):
    """Добавить тестовый доступ /testaccess"""
    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("❌ Только для администратора")
        return

    try:
        if context.args:
            user_id = int(context.args[0])
            days = int(context.args[1]) if len(context.args) > 1 else 7
        else:
            user_id = update.effective_user.id
            days = 7

        db.add_test_access(user_id, days)
        update.message.reply_text(f"✅ Тестовый доступ на {days} дней выдан пользователю {user_id}")
    except Exception as e:
        update.message.reply_text(f"❌ Ошибка: {e}")


# ========== ЗАПУСК БОТА ==========

def main():
    """Запуск бота"""
    try:
        # Инициализируем базу данных
        db.init_database()

        # Запускаем health server для Railway
        if IS_RAILWAY:
            health_thread = threading.Thread(target=start_health_server, daemon=True)
            health_thread.start()
            logger.info(f"✅ Health check сервер запущен на порту {PORT}")

        # Создаем updater
        updater = Updater(BOT_TOKEN, use_context=True)
        dispatcher = updater.dispatcher

        # Регистрируем команды
        dispatcher.add_handler(CommandHandler("start", start_command))
        dispatcher.add_handler(CommandHandler("help", help_command))
        dispatcher.add_handler(CommandHandler("stats", admin_stats_command))
        dispatcher.add_handler(CommandHandler("broadcast", broadcast_command))
        dispatcher.add_handler(CommandHandler("testaccess", test_access_command))
        dispatcher.add_handler(CommandHandler("ping", lambda u, c: u.message.reply_text("🏓 Pong!")))

        # Обработчики кнопок
        dispatcher.add_handler(CallbackQueryHandler(button_handler))

        # Обработчики оплаты
        dispatcher.add_handler(PreCheckoutQueryHandler(precheckout_handler))
        dispatcher.add_handler(MessageHandler(Filters.successful_payment, successful_payment_handler))

        # Обработчик ошибок
        def error_handler(update: Update, context: CallbackContext):
            logger.error(f"Ошибка: {context.error}")

        dispatcher.add_error_handler(error_handler)

        logger.info("✅ Все обработчики зарегистрированы")
        logger.info("🤖 Запускаем бота...")

        # Запускаем polling
        updater.start_polling(
            poll_interval=1.0,
            timeout=30,
            clean=True,
            bootstrap_retries=-1,
            read_latency=2.0
        )

        logger.info("✅ Бот успешно запущен и слушает команды!")
        logger.info(f"👉 Отправьте /start боту: https://t.me/{updater.bot.username}")

        if IS_RAILWAY:
            logger.info(f"🌐 Health check доступен по порту: {PORT}")

        # Бесконечный цикл
        updater.idle()

    except Exception as e:
        logger.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()