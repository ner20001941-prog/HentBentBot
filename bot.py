#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import io
import logging
from datetime import datetime
import os
from dotenv import load_dotenv

# Загружаем переменные окружения Railway
load_dotenv()

# Добавьте проверку для Railway
PORT = int(os.environ.get('PORT', 8000))
IS_RAILWAY = 'RAILWAY_ENVIRONMENT' in os.environ

# Устанавливаем кодировку UTF-8 для Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Импорты python-telegram-bot версии 13.x
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
    from config import BOT_TOKEN, TARIFFS, ADMIN_ID, CHANNEL_LINK, CHANNEL_ID
    import database as db
    import keyboards as kb
    print("✅ Конфигурация загружена")
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("Создайте файлы: config.py, database.py, keyboards.py")
    sys.exit(1)

# Настройка логгирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

print("=" * 60)
print("🤖 БОТ ПРОДАЖИ ДОСТУПА К КАНАЛУ ЗА ЗВЁЗДЫ")
print("=" * 60)
print(f"Токен: {BOT_TOKEN[:10]}...")
print(f"Админ: {ADMIN_ID}")
print(f"Канал: {CHANNEL_LINK}")
print("=" * 60)

# ========== ОСНОВНЫЕ КОМАНДЫ ==========

def start_command(update: Update, context: CallbackContext):
    """Команда /start - главное меню"""
    user = update.effective_user
    user_id = user.id
    
    # Инициализируем базу
    db.init_database()
    
    # Проверяем доступ
    has_access = db.has_channel_access(user_id)
    
    welcome_text = f"""
👋 <b>Привет, {user.first_name}!</b>

🌟 <b>Доступ к эксклюзивному каналу за Telegram Stars</b>

У нас есть:
• Приватный контент
• Эксклюзивные материалы
• Закрытое сообщество

{'✅ <b>У вас есть доступ к каналу!</b>' if has_access else '❌ <b>Доступа пока нет</b>'}
"""
    
    update.message.reply_text(
        welcome_text,
        reply_markup=kb.get_main_menu(has_access),
        parse_mode="HTML"
    )

def help_command(update: Update, context: CallbackContext):
    """Команда /help"""
    help_text = """
<b>🌟 Как купить доступ к каналу?</b>

1. <b>Выберите тариф</b> - нажмите "Купить доступ за звёзды"
2. <b>Оплатите Stars</b> - внутри Telegram
3. <b>Получите ссылку</b> - сразу после оплаты

<b>💎 Что такое Telegram Stars?</b>
Это внутренняя валюта Telegram для покупок.
Пополнить звёзды можно через @PremiumBot

<b>📱 Как оплатить?</b>
• Выберите тариф
• Нажмите "Оплатить"
• Подтвердите платёж в Telegram

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
        query.edit_message_text(
            text=f"👋 Главное меню\n\n{'✅ У вас есть доступ!' if has_access else '💎 Купите доступ за звёзды'}",
            reply_markup=kb.get_main_menu(has_access),
            parse_mode="HTML"
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
        
        # Отправляем счет для оплаты
        context.bot.send_invoice(
            chat_id=query.message.chat_id,
            title=tariff["name"],
            description=tariff["description"],
            payload=f"tariff_{tariff_id}_{user_id}",
            provider_token=None,  # Для Telegram Stars
            currency="XTR",  # Код для Telegram Stars
            prices=[LabeledPrice(tariff["name"], tariff["price"])],
            start_parameter=tariff_id,
            need_name=False,
            need_phone_number=False,
            need_email=False,
            need_shipping_address=False,
            is_flexible=False
        )
    
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
            if expires_at:
                expiry_date = datetime.fromisoformat(expires_at)
                days_left = (expiry_date - datetime.now()).days
                status_text = f"✅ Активен ({days_left} дней осталось)"
            else:
                status_text = "✅ Бессрочный доступ"
            
            text = f"<b>📊 Ваш доступ:</b>\n\nСтатус: {status_text}\nОплачено: ✅ Да"
        else:
            text = "❌ <b>У вас нет активного доступа</b>\n\nКупите подписку, чтобы получить ссылку на канал."
        
        query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💎 Купить доступ", callback_data="buy_access")],
                [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]
            ]),
            parse_mode="HTML"
        )
    
    # КНОПКА ПОМОЩЬ
    elif data == "help":
        query.edit_message_text(
            text=help_command.__doc__.replace('    ', ''),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💎 Купить доступ", callback_data="buy_access")],
                [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]
            ]),
            parse_mode="HTML"
        )
    
    # КНОПКА ПРЕДПРОСМОТР
    elif data == "preview":
        query.edit_message_text(
            text="<b>👁️ Предпросмотр канала</b>\n\nК сожалению, предпросмотр приватного канала недоступен.\n\nНо вы можете купить доступ и убедиться в качестве контента!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💎 Купить доступ", callback_data="buy_access")],
                [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]
            ]),
            parse_mode="HTML"
        )

# ========== ОБРАБОТКА ОПЛАТЫ ==========

def precheckout_handler(update: Update, context: CallbackContext):
    """Подтверждение оплаты"""
    query = update.pre_checkout_query
    
    # Проверяем, что это наш товар
    if query.invoice_payload.startswith("tariff_"):
        query.answer(ok=True)
    else:
        query.answer(ok=False, error_message="Ошибка оплаты")

def successful_payment_handler(update: Update, context: CallbackContext):
    """Успешная оплата - выдаём доступ"""
    payment = update.message.successful_payment
    user_id = update.effective_user.id
    
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

<b>⚠️ Важно:</b> Не передавайте ссылку третьим лицам.
"""
                
                update.message.reply_text(
                    success_text,
                    parse_mode="HTML",
                    disable_web_page_preview=False,
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔗 Открыть канал", url=CHANNEL_LINK)],
                        [InlineKeyboardButton("📊 Мой доступ", callback_data="my_access")]
                    ])
                )
                
                # Уведомление админу
                try:
                    context.bot.send_message(
                        ADMIN_ID,
                        f"💰 <b>Новая продажа!</b>\n\n"
                        f"👤 Пользователь: {update.effective_user.mention_html()}\n"
                        f"📦 Тариф: {tariff['name']}\n"
                        f"💎 Сумма: {payment.total_amount} звезд\n"
                        f"🆔 ID: {user_id}",
                        parse_mode="HTML"
                    )
                except:
                    pass

# ========== АДМИН КОМАНДЫ ==========

def admin_stats_command(update: Update, context: CallbackContext):
    """Статистика для админа /stats"""
    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("❌ Только для администратора")
        return
    
    users = db.load_users()
    total_users = len(users)
    active_users = db.get_active_users_count()
    
    stats_text = f"""
<b>📊 Статистика бота:</b>

👥 Всего пользователей: {total_users}
✅ С активным доступом: {active_users}
💰 Тарифов: {len(TARIFFS)}

<b>Тарифы:</b>
"""
    
    for tariff_id, tariff in TARIFFS.items():
        stats_text += f"• {tariff['name']}: {tariff['price']} ⭐\n"
    
    update.message.reply_text(stats_text, parse_mode="HTML")

# ========== ЗАПУСК БОТА ==========

def main():
    """Запуск бота"""
    try:
        # Создаем бота
        updater = Updater(BOT_TOKEN, use_context=True)
        dispatcher = updater.dispatcher
        
        # Регистрируем обработчики (код как был)...
        dispatcher.add_handler(CommandHandler("start", start_command))
        dispatcher.add_handler(CommandHandler("help", help_command))
        dispatcher.add_handler(CommandHandler("stats", admin_stats_command))
        dispatcher.add_handler(CallbackQueryHandler(button_handler))
        dispatcher.add_handler(PreCheckoutQueryHandler(precheckout_handler))
        dispatcher.add_handler(MessageHandler(Filters.successful_payment, successful_payment_handler))
        
        # Запускаем
        print("=" * 60)
        print("🚂 БОТ ЗАПУЩЕН НА RAILWAY" if IS_RAILWAY else "💻 БОТ ЗАПУЩЕН ЛОКАЛЬНО")
        print("=" * 60)
        print(f"🌐 PORT: {PORT}")
        print(f"🤖 Токен: {BOT_TOKEN[:10]}...")
        print(f"👤 Админ: {ADMIN_ID}")
        print("=" * 60)
        
        # Запускаем polling
        updater.start_polling()
        
        # Для Railway добавляем веб-сервер для health checks
        if IS_RAILWAY:
            from http.server import HTTPServer, BaseHTTPRequestHandler
            import threading
            
            class HealthHandler(BaseHTTPRequestHandler):
                def do_GET(self):
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b'OK')
                def log_message(self, format, *args):
                    pass
            
            def run_http_server():
                server = HTTPServer(('0.0.0.0', PORT), HealthHandler)
                print(f"🌐 HTTP сервер запущен на порту {PORT}")
                server.serve_forever()
            
            # Запускаем HTTP сервер в отдельном потоке
            http_thread = threading.Thread(target=run_http_server, daemon=True)
            http_thread.start()
            print(f"✅ Health check сервер запущен на порту {PORT}")
        
        print("🤖 Бот запущен и готов принимать платежи!")
        print("👉 Отправьте /start боту в Telegram")
        
        updater.idle()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        
if __name__ == "__main__":
    # Инициализируем базу
    db.init_database()
    main()