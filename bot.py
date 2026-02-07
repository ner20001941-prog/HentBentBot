import asyncio
import sys
import os
import io
import logging
from datetime import datetime
import time
from datetime import datetime, time as datetime_time  

import logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)


# Устанавливаем кодировку UTF-8 для Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Фикс для Windows PRN ошибки
if sys.platform == 'win32':
    sys.stderr = open(os.devnull, 'w')
else:
    sys.stderr = io.StringIO()

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update, LabeledPrice
from telegram.ext import (
    Updater,  
    CommandHandler,
    CallbackQueryHandler,
    PreCheckoutQueryHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    JobQueue
)

# Импортируем наши модули
from config import BOT_TOKEN, TARIFFS, ADMIN_ID, CHANNEL_LINK
import database as db
import keyboards as kb

# Настройка логгирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

print("=== DEBUG: Все импорты загружены ===")

# ========== КОМАНДЫ БОТА ==========

async def start_command(update: Update, context: CallbackContext):
    """Обработчик команды /start"""
    user = update.effective_user
    user_id = user.id
    
    # Инициализируем базу данных
    db.init_database()
    
    # Проверяем есть ли у пользователя доступ к каналу
    has_access = db.has_channel_access(user_id)
    
    # Приветственное сообщение
    welcome_text = f"""
👋 Привет, {user.first_name}!

🔒 **Доступ к приватному каналу**

Получите доступ к эксклюзивному контенту:
• Приватные материалы
• Эксклюзивный контент
• Закрытое сообщество

{'✅ У вас уже есть доступ к каналу!' if has_access else '❌ У вас пока нет доступа'}
"""
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=kb.get_main_menu(has_access),
        parse_mode="Markdown"
    )
    
async def help_command(update: Update, context: CallbackContext):
    """Обработчик команды /help"""
    help_text = """
🤔 **Как это работает?**

1. **Выберите тариф** — 1 месяц, 3 месяца или навсегда
2. **Оплатите Telegram Stars** — внутри Telegram
3. **Получите ссылку на канал** — сразу после оплаты

⭐ **Что такое Telegram Stars?**
Это внутренняя валюта Telegram для покупок.
Пополнить звёзды можно через @PremiumBot

💳 **Как оплатить?**
• Нажмите "Купить доступ"
• Выберите тариф
• Подтвердите оплату

🔗 **Доступ к каналу:**
После оплаты в меню появится кнопка "Получить ссылку на канал"

❓ **Проблемы с оплатой?**
Напишите в поддержку: @ваша_поддержка
"""
    
    await update.message.reply_text(help_text, parse_mode="Markdown")

# ========== ТАРИФЫ И ОПЛАТА ==========

async def show_tariffs(update: Update, context: CallbackContext):
    """Показать тарифы"""
    query = update.callback_query
    await query.answer()
    
    tariffs_text = """
📋 **Доступные тарифы:**

Выберите подходящий вариант:
"""
    
    for tariff_id, tariff_info in TARIFFS.items():
        duration = "∞" if tariff_info.get("days") is None else f"{tariff_info['days']} дней"
        
        tariffs_text += f"""
**{tariff_info['name']}** — {tariff_info['price']} ⭐
📅 {duration}
{tariff_info.get('description', '')}
"""
    
    await query.edit_message_text(
        text=tariffs_text,
        reply_markup=kb.get_tariffs_keyboard(),
        parse_mode="Markdown"
    )

async def buy_tariff(update: Update, context: CallbackContext):
    """Начать процесс покупки"""
    query = update.callback_query
    await query.answer()
    
    tariff_id = query.data.replace("buy_", "")
    tariff = TARIFFS.get(tariff_id)
    
    if not tariff:
        await query.answer("❌ Тариф не найден", show_alert=True)
        return
    
    # Отправляем счет
    await context.bot.send_invoice(
        chat_id=update.effective_chat.id,
        title=tariff["name"],
        description=tariff["description"],
        payload=f"tariff_{tariff_id}",
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

async def pre_checkout(update: Update, context: CallbackContext):
    """Подтверждение оплаты"""
    query = update.pre_checkout_query
    
    # Проверяем payload
    if query.invoice_payload.startswith("tariff_"):
        await query.answer(ok=True)
    else:
        await query.answer(ok=False, error_message="Ошибка оплаты")

async def successful_payment(update: Update, context: CallbackContext):
    """Успешная оплата - отправляем ссылку на канал"""
    payment = update.message.successful_payment
    user_id = update.effective_user.id
    
    # Извлекаем ID тарифа
    if payment.invoice_payload.startswith("tariff_"):
        tariff_id = payment.invoice_payload.replace("tariff_", "")
        tariff = TARIFFS.get(tariff_id)
        
        if not tariff:
            return
        
        # Добавляем доступ к каналу
        db.add_channel_access(user_id, tariff_id)
        
        # Отправляем подтверждение и ссылку на канал
        success_text = f"""
✅ **Оплата прошла успешно!**

Спасибо за покупку! Вы приобрели:
**{tariff['name']}**

🔗 **Ссылка на канал:**
{CHANNEL_LINK}

📋 **Инструкция:**
1. Нажмите на ссылку выше
2. Вступите в канал
3. Наслаждайтесь контентом!

⚠️ **Важно:** Не передавайте ссылку третьим лицам
"""
        
        await update.message.reply_text(
            success_text,
            parse_mode="Markdown",
            disable_web_page_preview=False
        )
        
        # Уведомление админу
        try:
            await context.bot.send_message(
                ADMIN_ID,
                f"💰 Новая покупка доступа к каналу!\n"
                f"Пользователь: {update.effective_user.username or update.effective_user.id}\n"
                f"Тариф: {tariff['name']}\n"
                f"Сумма: {payment.total_amount} звезд"
            )
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления админу: {e}")

# ========== КАНАЛ МЕНЮ ==========

async def send_channel_link(update: Update, context: CallbackContext):
    """Отправить ссылку на канал (если есть доступ)"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # Проверяем доступ
    has_access = db.has_channel_access(user_id)
    
    if not has_access:
        await query.message.reply_text(
            "❌ У вас нет доступа к каналу!\n\n"
            "Приобретите подписку, чтобы получить ссылку.",
            reply_markup=kb.get_main_menu(False)
        )
        return
    
    # Отправляем ссылку на канал
    channel_text = f"""
🔗 **Доступ к приватному каналу**

Ваша ссылка:
{CHANNEL_LINK}

📋 **Инструкция:**
1. Нажмите на ссылку выше
2. Если не подписаны - подпишитесь
3. Если уже подписаны - просто зайдите

⏰ **Срок доступа:**
{db.get_access_expiry(user_id)}
"""
    
    await query.edit_message_text(
        text=channel_text,
        parse_mode="Markdown",
        disable_web_page_preview=False,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Проверить доступ", callback_data="check_access")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]
        ])
    )

# ========== АДМИН КОМАНДЫ ==========

async def admin_stats(update: Update, context: CallbackContext):
    """Статистика для админа"""
    if update.effective_user.id != ADMIN_ID:
        return
    
    users = db.load_users()
    total_users = len(users)
    
    # Считаем пользователей с доступом к каналу
    users_with_access = 0
    active_subs = 0
    expired_subs = 0
    
    for user_data in users.values():
        if "channel_access" in user_data:
            users_with_access += 1
            
            # Проверяем активен ли доступ
            access_data = user_data["channel_access"]
            expires_at = access_data.get("expires_at")
            
            if expires_at:
                try:
                    expiry_date = datetime.fromisoformat(expires_at)
                    if datetime.now() < expiry_date:
                        active_subs += 1
                    else:
                        expired_subs += 1
                except:
                    active_subs += 1
            else:
                active_subs += 1  # Бессрочный доступ
    
    stats_text = f"""
📊 **Статистика бота (канал):**

👥 Всего пользователей: {total_users}
🔒 С доступом к каналу: {users_with_access}
✅ Активных подписок: {active_subs}
❌ Истекших подписок: {expired_subs}

🔗 Канал: {CHANNEL_LINK}

⚙️ **Команды админа:**
/give <user_id> <tariff_id> - выдать доступ
/cleanup - очистка истекших подписок
"""
    
    await update.message.reply_text(stats_text, parse_mode="Markdown")

async def cleanup_command(update: Update, context: CallbackContext):
    """Очистка истекших подписок"""
    if update.effective_user.id != ADMIN_ID:
        return
    
    cleaned = db.cleanup_expired()
    await update.message.reply_text(f"✅ Очищено {cleaned} истекших подписок")

async def give_subscription(update: Update, context: CallbackContext):
    """Выдать доступ к каналу (админ команда)"""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Только для администратора")
        return

    if len(context.args) < 2:
        await update.message.reply_text(
            "Использование:\n/give <user_id> <tariff_id>\n\n"
            "Пример:\n/give 123456789 1_month\n\n"
            "Доступные тарифы:\n" + 
            "\n".join([f"- {tid}: {t['name']}" for tid, t in TARIFFS.items()])
        )
        return

    try:
        user_id = int(context.args[0])
        tariff_id = context.args[1]

        if tariff_id not in TARIFFS:
            await update.message.reply_text("❌ Такого тарифа нет")
            return

        # Выдаем доступ к каналу
        db.add_channel_access(user_id, tariff_id)

        await update.message.reply_text(
            f"✅ Доступ **{TARIFFS[tariff_id]['name']}** выдан пользователю `{user_id}`\n\n"
            f"Ссылка на канал: {CHANNEL_LINK}",
            parse_mode="Markdown"
        )

    except ValueError:
        await update.message.reply_text("❌ user_id должен быть числом")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

async def debug_menu(update: Update, context: CallbackContext):
    """Отладка меню"""
    user_id = update.effective_user.id
    has_access = db.has_channel_access(user_id)
    
    text = f"""
🔧 **Отладка меню:**
User ID: {user_id}
Доступ к каналу: {'✅ Есть' if has_access else '❌ Нет'}
"""
    
    await update.message.reply_text(
        text,
        reply_markup=kb.get_main_menu(has_access),
        parse_mode="Markdown"
    )

# ========== ОБРАБОТЧИК КНОПОК ==========

async def handle_callback(update: Update, context: CallbackContext):
    """Обработчик всех callback кнопок"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    print(f"🔘 Нажата кнопка: {data}")
    
    try:
        # КНОПКА НАЗАД
        if data in ["back_to_main", "back_to_start"]:
            user_id = update.effective_user.id
            has_access = db.has_channel_access(user_id)
            
            welcome_text = f"""
Привет, {update.effective_user.first_name}!

🔒 **Доступ к приватному каналу**

{'✅ У вас есть доступ к каналу!' if has_access else '❌ У вас пока нет доступа'}
"""
            
            await query.edit_message_text(
                text=welcome_text,
                reply_markup=kb.get_main_menu(has_access),
                parse_mode="Markdown"
            )
            return
        
        # КНОПКА КУПИТЬ ДОСТУП
        elif data == "buy_access":
            await show_tariffs(update, context)
        
        # КНОПКИ ПОКУПКИ ТАРИФОВ
        elif data.startswith("buy_"):
            await buy_tariff(update, context)
        
        # КНОПКА ПОЛУЧИТЬ ССЫЛКУ НА КАНАЛ
        elif data == "get_channel_link":
            await send_channel_link(update, context)
        
        # КНОПКА МОЙ ДОСТУП
        elif data == "my_access":
            user_id = update.effective_user.id
            expiry_info = db.get_access_expiry(user_id)
            
            text = f"""
📊 **Информация о вашем доступе:**

{expiry_info}

{'🔗 Нажмите "Получить ссылку на канал" чтобы получить доступ' if 'Нет' not in expiry_info else '❌ У вас нет активного доступа'}
"""
            
            await query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔗 Получить ссылку", callback_data="get_channel_link")],
                    [InlineKeyboardButton("💰 Купить доступ", callback_data="buy_access")],
                    [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]
                ])
            )
        
        # КНОПКА ПРОВЕРИТЬ ДОСТУП
        elif data == "check_access":
            user_id = update.effective_user.id
            has_access = db.has_channel_access(user_id)
            
            if has_access:
                await query.answer("✅ Доступ активен!", show_alert=True)
            else:
                await query.answer("❌ Доступа нет или истек", show_alert=True)
        
        # КНОПКА ПРИМЕР (preview)
        elif data == "preview":
            preview_text = """
👁️‍🗨️ **Предпросмотр канала**

К сожалению, предпросмотр приватного канала недоступен.

Но вы можете:
1. Приобрести подписку
2. Получить доступ к эксклюзивному контенту
3. Вступить в закрытое сообщество

Стоимость доступа от 100 звезд.
"""
            await query.edit_message_text(
                text=preview_text,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("💰 Купить доступ", callback_data="buy_access")],
                    [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]
                ])
            )
        
        # КНОПКА ПОМОЩЬ
        elif data == "help":
            help_text = """
🤔 **Как это работает?**

1. **Выберите тариф** — 1 месяц, 3 месяца или навсегда
2. **Оплатите Telegram Stars** — внутри Telegram
3. **Получите ссылку на канал** — сразу после оплаты

⭐ **Что такое Telegram Stars?**
Это внутренняя валюта Telegram для покупок.
Пополнить звёзды можно через @PremiumBot

💳 **Как оплатить?**
• Нажмите "Купить доступ"
• Выберите тариф
• Подтвердите оплату

🔗 **Доступ к каналу:**
После оплаты в меню появится кнопка "Получить ссылку на канал"

❓ **Проблемы с оплатой?**
Напишите в поддержку
"""
            await query.edit_message_text(
                text=help_text,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]
                ])
            )
        
        # НЕИЗВЕСТНАЯ КНОПКА
        else:
            await query.answer(f"❌ Неизвестная кнопка: {data}", show_alert=True)
    
    except Exception as e:
        print(f"Ошибка обработки callback: {e}")
        await query.answer("❌ Произошла ошибка", show_alert=True)

# ========== ФОНОВЫЕ ЗАДАЧИ ==========

async def daily_cleanup(update: Update, context: CallbackContext):
    """Ежедневная очистка"""
    cleaned = db.cleanup_expired()
    if cleaned > 0:
        logger.info(f"Ежедневная очистка: удалено {cleaned} подписок")

# ========== ТЕСТОВЫЕ КОМАНДЫ ДЛЯ ПРОВЕРКИ ==========

async def test_link_command(update: Update, context: CallbackContext):
    """Тестовая команда для проверки выдачи ссылки"""
    await update.message.reply_text(
        f"🔗 Тестовая ссылка:\n{CHANNEL_LINK}\n\n"
        f"Кликайте на ссылку выше!",
        disable_web_page_preview=False
    )

async def give_me_access(update: Update, context: CallbackContext):
    """Выдать себе доступ (только админу)"""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Только для администратора")
        return
    
    user_id = update.effective_user.id
    db.add_channel_access(user_id, "1_month")
    
    await update.message.reply_text(
        f"✅ Вам выдан тестовый доступ на 1 месяц!\n\n"
        f"Теперь нажмите /testlink для получения ссылки\n"
        f"Или кнопку в меню",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 Получить ссылку", callback_data="get_channel_link")]
        ])
    )

async def check_my_access(update: Update, context: CallbackContext):
    """Проверить мой доступ"""
    user_id = update.effective_user.id
    has_access = db.has_channel_access(user_id)
    
    status = "✅ АКТИВЕН" if has_access else "❌ НЕТ ДОСТУПА"
    
    await update.message.reply_text(
        f"📊 Ваш статус:\n\n"
        f"ID: {user_id}\n"
        f"Доступ: {status}\n\n"
        f"Ссылка: {CHANNEL_LINK}",
        disable_web_page_preview=False
    )

async def full_test(update: Update, context: CallbackContext):
    """Полная проверка"""
    user_id = update.effective_user.id
    is_admin = user_id == ADMIN_ID
    
    # 1. Выдаем доступ если админ
    if is_admin:
        db.add_channel_access(user_id, "forever")
    
    # 2. Проверяем
    has_access = db.has_channel_access(user_id)
    
    # 3. Отправляем тест
    await update.message.reply_text(
        f"🧪 ТЕСТ ВЫДАЧИ ССЫЛКИ\n\n"
        f"1. Вы администратор: {'✅ ДА' if is_admin else '❌ НЕТ'}\n"
        f"2. Доступ в базе: {'✅ ВЫДАН' if has_access else '❌ НЕТ'}\n"
        f"3. Ссылка будет ниже ↓",
        parse_mode="Markdown"
    )
    
    # 4. ПРЯМАЯ ВЫДАЧА ССЫЛКИ
    await update.message.reply_text(
        f"🔗 ССЫЛКА НА КАНАЛ:\n{CHANNEL_LINK}",
        disable_web_page_preview=False
    )

async def check_access(update: Update, context: CallbackContext):
    """Проверить статус доступа"""
    user_id = update.effective_user.id
    has_access = db.has_channel_access(user_id)
    expiry_info = db.get_access_expiry(user_id)
    
    check_text = f"""
📊 **СТАТУС ДОСТУПА:**

ID пользователя: {user_id}
Доступ к каналу: {'✅ АКТИВЕН' if has_access else '❌ ОТСУТСТВУЕТ'}
Информация: {expiry_info}

**Ссылка на канал:**
{CHANNEL_LINK}

**Что делать если нет доступа:**
1. Нажмите /givemeaccess (админ)
2. Или купите доступ через меню
"""
    
    await update.message.reply_text(
        check_text,
        parse_mode="Markdown",
        disable_web_page_preview=False,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 Получить ссылку", callback_data="get_channel_link")],
            [InlineKeyboardButton("💎 Выдать доступ", callback_data="get_access")]
        ])
    )

async def get_channel_info(update: Update, context: CallbackContext):
    """Получить информацию о канале"""
    if update.effective_user.id != ADMIN_ID:
        return
    
    # Укажите юзернейм или ID канала
    channel_username = "@username_вашего_канала"  # или ссылку
    
    try:
        chat = await context.bot.get_chat(channel_username)
        info = f"""
📊 **Информация о канале:**

ID: `{chat.id}`
Название: {chat.title}
Юзернейм: {chat.username}
Тип: {chat.type}
Описание: {chat.description or 'Нет описания'}

**Для использования в коде:**
CHANNEL_ID = {chat.id}
"""
        await update.message.reply_text(info, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

async def remove_user_from_channel(user_id: int, Update, context: CallbackContext):
    """Исключить пользователя из канала"""
    try:
        from config import CHANNEL_ID
        
        # Пробуем исключить из канала
        await context.bot.ban_chat_member(
            chat_id=CHANNEL_ID,
            user_id=user_id,
            until_date=int(time.time()) + 60  # Бан на 60 секунд
        )
        
        # Сразу разбаниваем (исключаем, но оставляем возможность вступить снова)
        await context.bot.unban_chat_member(
            chat_id=CHANNEL_ID,
            user_id=user_id,
            only_if_banned=True
        )
        
        logger.info(f"Пользователь {user_id} исключен из канала")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка исключения пользователя {user_id}: {e}")
        return False
async def check_expired_subscriptions(update: Update, context: CallbackContext):
    """Проверка истекших подписок и исключение из канала"""
    logger.info("🔍 Проверка истекших подписок...")
    
    users = db.load_users()
    expired_count = 0
    removed_count = 0
    
    for user_key, user_data in users.items():
        if "channel_access" in user_data:
            access_data = user_data["channel_access"]
            expires_at = access_data.get("expires_at")
            
            if expires_at:
                try:
                    expiry_date = datetime.fromisoformat(expires_at)
                    
                    # Если подписка истекла
                    if datetime.now() > expiry_date:
                        expired_count += 1
                        
                        # Исключаем из канала
                        user_id = int(user_key)
                        removed = await remove_user_from_channel(user_id, context)
                        
                        if removed:
                            removed_count += 1
                            logger.info(f"✅ Пользователь {user_id} исключен из канала")
                            
                            # Отправляем уведомление пользователю
                            try:
                                await context.bot.send_message(
                                    chat_id=user_id,
                                    text="⚠️ *Ваша подписка истекла*\n\n"
                                         "Доступ к приватному каналу был отозван.\n"
                                         "Для продления используйте /start",
                                    parse_mode="Markdown"
                                )
                            except:
                                pass
                            
                except Exception as e:
                    logger.error(f"Ошибка проверки пользователя {user_key}: {e}")
    
    logger.info(f"Проверка завершена: {expired_count} истекло, {removed_count} исключено")
    
    # Уведомление админу
    if expired_count > 0:
        try:
            await context.bot.send_message(
                ADMIN_ID,
                f"📊 Ежедневная проверка подписок:\n"
                f"• Истекших подписок: {expired_count}\n"
                f"• Исключено из канала: {removed_count}"
            )
        except:
            pass
async def manual_check(update: Update, context: CallbackContext):
    """Ручная проверка и исключение"""
    if update.effective_user.id != ADMIN_ID:
        return
    
    await update.message.reply_text("🔍 Запускаю ручную проверку...")
    
    # Создаем контекст для задачи
    from functools import partial
    await check_expired_subscriptions(context)
    
    await update.message.reply_text("✅ Проверка завершена")

async def view_expired(update: Update, context: CallbackContext):
    """Посмотреть истекшие подписки"""
    if update.effective_user.id != ADMIN_ID:
        return
    
    expired_users = db.get_expired_users()
    
    if not expired_users:
        await update.message.reply_text("✅ Нет истекших подписок")
        return
    
    text = "📋 *Истекшие подписки:*\n\n"
    
    for i, user in enumerate(expired_users[:50], 1):  # Ограничим 50 записей
        text += f"{i}. ID: `{user['user_id']}`\n"
        text += f"   Тариф: {user.get('tariff_id', 'неизвестно')}\n"
        text += f"   Истек: {user['expired_at'][:10]}\n\n"
    
    text += f"\nВсего: {len(expired_users)} пользователей"
    
    await update.message.reply_text(text, parse_mode="Markdown")
async def backup_database(update: Update, context: CallbackContext):
    """Резервное копирование базы данных"""
    import shutil
    from datetime import datetime
    
    try:
        backup_file = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        shutil.copy2("user_data.json", backup_file)
        
        logger.info(f"✅ Создан бэкап: {backup_file}")
        
        # Удаляем старые бэкапы (оставляем последние 7)
        import os
        import glob
        
        backup_files = sorted(glob.glob("backup_*.json"))
        if len(backup_files) > 7:
            for old_backup in backup_files[:-7]:
                os.remove(old_backup)
                logger.info(f"🗑️ Удален старый бэкап: {old_backup}")
                
    except Exception as e:
        logger.error(f"❌ Ошибка создания бэкапа: {e}")

async def ping(update: Update, context: CallbackContext):
    """Простая тестовая команда"""
    print(f"📨 Получена команда ping от {update.effective_user.id}")
    try:
        await update.message.reply_text("🏓 Pong! Бот работает!")
        print("✅ Сообщение отправлено")
    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")

def main():
    print("=== DEBUG: Функция main() вызвана ===")
    
    try:
        print("=== DEBUG: Создаем приложение ===")
        # Создаем приложение НОВЫМ способом
        application = application.builder().token(BOT_TOKEN).build()
        
        print("=== DEBUG: Добавляем обработчики команд ===")
        # Добавляем обработчики команд
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("admin_stats", admin_stats))
        application.add_handler(CommandHandler("cleanup", cleanup_command))
        application.add_handler(CommandHandler("ping", ping))
        
        print("=== DEBUG: Добавляем обработчики оплаты ===")
        # Обработчики оплаты
        application.add_handler(PreCheckoutQueryHandler(pre_checkout))
        application.add_handler(MessageHandler(Filters.successful_payment, successful_payment))
        
        print("=== DEBUG: Добавляем обработчики кнопок ===")
        # Обработчики кнопок
        application.add_handler(CallbackQueryHandler(handle_callback))
        
        print("=== DEBUG: Добавляем команды админа ===")
        # Команды админа
        application.add_handler(CommandHandler("give", give_subscription))
        application.add_handler(CommandHandler("debug", debug_menu))
        
        print("=== DEBUG: Добавляем тестовые команды ===")
        # Тестовые команды
        application.add_handler(CommandHandler("testlink", test_link_command))
        application.add_handler(CommandHandler("givemeaccess", give_me_access))
        application.add_handler(CommandHandler("checkaccess", check_access))
        application.add_handler(CommandHandler("fulltest", full_test))
        application.add_handler(CommandHandler("channelinfo", get_channel_info))
        
        print("=== DEBUG: Запускаем polling ===")
        # Запускаем бота
        print("=" * 50)
        print(" Бот запущен успешно!")
        print("=" * 50)
        
        # НОВЫЙ СПОСОБ запуска для версии 20.x
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )
        
    except Exception as e:
        print(f"=== DEBUG: КРИТИЧЕСКАЯ ОШИБКА: {e} ===")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=== DEBUG: Запуск из __main__ ===")
    main()

import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OK')
    
    def log_message(self, format, *args):
        pass  # Отключаем логи

def start_http_server():
    """Запуск простого HTTP сервера для health checks"""
    server = HTTPServer(('0.0.0.0', 8000), HealthHandler)
    server.serve_forever()
