import asyncio
import sys
import os
import io
from datetime import datetime, time, timedelta
import logging

# Фикс для Windows PRN ошибки
if sys.platform == 'win32':
    sys.stderr = open(os.devnull, 'w')
else:
    sys.stderr = io.StringIO()

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update, LabeledPrice
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    PreCheckoutQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    JobQueue
)

# Импортируем наши модули
from config import BOT_TOKEN, TARIFFS, VIDEOS, ADMIN_ID
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

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    user_id = user.id
    
    # Инициализируем базу данных
    db.init_database()
    
    # Проверяем есть ли у пользователя доступ
    user_videos = db.get_user_videos(user_id)
    has_access = len(user_videos) > 0
    
    # Приветственное сообщение
    welcome_text = f"""
👋 Привет, {user.first_name}!

🎬 Добро пожаловать в видеотеку!

Здесь ты можешь получить доступ к эксклюзивным видео-материалам.

💰 Оплата происходит через Telegram Stars — это быстро и безопасно!

{"" if has_access else "❌ У тебя пока нет доступа к видео. Приобрети подписку!"}
"""
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=kb.get_main_menu(user_has_access=has_access),
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = """
🤔 **Как это работает?**

1. **Выберите тариф** — 1 месяц, 3 месяца или навсегда
2. **Оплатите Telegram Stars** — внутри Telegram
3. **Смотрите видео** — сразу после оплаты

⭐ **Что такое Telegram Stars?**
Это внутренняя валюта Telegram для покупок.
Пополнить звёзды можно через @PremiumBot

💳 **Как оплатить?**
• Нажмите "Купить доступ"
• Выберите тариф
• Подтвердите оплату

🎬 **Доступ к видео:**
После оплаты в меню появится кнопка "Мои видео"

❓ **Проблемы с оплатой?**
Напишите в поддержку: @ваша_поддержка
"""
    
    await update.message.reply_text(help_text, parse_mode="Markdown")

# ========== ТАРИФЫ И ОПЛАТА ==========

async def show_tariffs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать тарифы"""
    query = update.callback_query
    await query.answer()
    
    tariffs_text = """
📋 **Доступные тарифы:**

Выберите подходящий вариант:
"""
    
    for tariff_id, tariff_info in TARIFFS.items():
        videos_count = len(tariff_info.get("videos", []))
        duration = "∞" if tariff_info.get("days") is None else tariff_info["days"]
        
        tariffs_text += f"""
**{tariff_info['name']}** — {tariff_info['price']} ⭐
📅 {duration} дней
🎬 {videos_count} видео
{tariff_info.get('description', '')}
"""
    
    await query.edit_message_text(
        text=tariffs_text,
        reply_markup=kb.get_tariffs_keyboard(),
        parse_mode="Markdown"
    )

async def buy_tariff(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

async def pre_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подтверждение оплаты"""
    query = update.pre_checkout_query
    
    # Проверяем payload
    if query.invoice_payload.startswith("tariff_"):
        await query.answer(ok=True)
    else:
        await query.answer(ok=False, error_message="Ошибка оплаты")

async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Успешная оплата"""
    payment = update.message.successful_payment
    user_id = update.effective_user.id
    
    # Извлекаем ID тарифа
    if payment.invoice_payload.startswith("tariff_"):
        tariff_id = payment.invoice_payload.replace("tariff_", "")
        
        # Добавляем подписку пользователю
        db.add_subscription(user_id, tariff_id)
        
        # Отправляем подтверждение
        success_text = f"""
✅ **Оплата прошла успешно!**

Спасибо за покупку! Вы приобрели:
**{TARIFFS[tariff_id]['name']}**

Теперь у вас есть доступ к {len(TARIFFS[tariff_id].get('videos', []))} видео.

Нажмите "Мои видео" чтобы начать просмотр!
"""
        
        await update.message.reply_text(
            success_text,
            reply_markup=kb.get_main_menu(True),
            parse_mode="Markdown"
        )
        
        # Уведомление админу
        try:
            await context.bot.send_message(
                ADMIN_ID,
                f"💰 Новая покупка!\n"
                f"Пользователь: {update.effective_user.username or update.effective_user.id}\n"
                f"Тариф: {TARIFFS[tariff_id]['name']}\n"
                f"Сумма: {payment.total_amount} звезд"
            )
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления админу: {e}")

# ========== ВИДЕО МЕНЮ ==========

async def show_videos_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать меню с видео"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    video_ids = db.get_user_videos(user_id)
    
    if not video_ids:
        await query.edit_message_text(
            "❌ У вас нет доступа к видео.\nПриобретите подписку!",
            reply_markup=kb.get_main_menu(False)
        )
        return
    
    # Формируем список видео
    videos_text = "🎬 **Ваши видео:**\n\n"
    for i, video_id in enumerate(video_ids, 1):
        if video_id in VIDEOS:
            videos_text += f"{i}. {VIDEOS[video_id]['title']}\n"
    
    await query.edit_message_text(
        text=videos_text,
        reply_markup=kb.get_videos_keyboard(video_ids),
        parse_mode="Markdown"
    )

async def send_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправить видео"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    video_id = query.data.replace("watch_", "")
    
    # Проверяем доступ
    user_videos = db.get_user_videos(user_id)
    
    if video_id not in user_videos:
        await query.message.reply_text(
            "❌ У вас нет доступа к этому видео!",
            reply_markup=kb.get_main_menu(False)
        )
        return
    
    # Отправляем видео
    video_info = VIDEOS.get(video_id)
    
    if not video_info:
        await query.answer("❌ Видео не найдено", show_alert=True)
        return
    
    try:
        with open(video_info["file_path"], 'rb') as video_file:
            await context.bot.send_video(
                chat_id=update.effective_chat.id,
                video=video_file,
                caption=f"**{video_info['title']}**\n{video_info['description']}",
                parse_mode="Markdown",
                supports_streaming=True
            )
    except Exception as e:
        logger.error(f"Ошибка отправки видео: {e}")
        await query.message.reply_text(
            "❌ Ошибка при отправке видео. Попробуйте позже."
        )

# ========== АДМИН КОМАНДЫ ==========

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статистика для админа"""
    if update.effective_user.id != ADMIN_ID:
        return
    
    users = db.load_users()
    total_users = len(users)
    total_subs = sum(len(user.get("subscriptions", {})) for user in users.values())
    
    stats_text = f"""
📊 **Статистика бота:**

👥 Всего пользователей: {total_users}
💰 Всего подписок: {total_subs}
🗃️ Размер базы: {len(str(users)) // 1024} KB

⚙️ Команды админа:
/admin_stats - эта статистика
/cleanup - очистка истекших подписок
/backup - бэкап базы
"""
    
    await update.message.reply_text(stats_text, parse_mode="Markdown")

async def cleanup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Очистка истекших подписок"""
    if update.effective_user.id != ADMIN_ID:
        return
    
    cleaned = db.cleanup_expired()
    await update.message.reply_text(f"✅ Очищено {cleaned} истекших подписок")

# ========== ФОНОВЫЕ ЗАДАЧИ ==========

async def daily_cleanup(context: ContextTypes.DEFAULT_TYPE):
    """Ежедневная очистка"""
    cleaned = db.cleanup_expired()
    if cleaned > 0:
        logger.info(f"Ежедневная очистка: удалено {cleaned} подписок")

async def backup_database(context: ContextTypes.DEFAULT_TYPE):
    """Бэкап базы данных"""
    import shutil
    from datetime import datetime
    
    backup_file = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    shutil.copy2("user_data.json", backup_file)
    
    logger.info(f"Создан бэкап: {backup_file}")

# ========== ОБРАБОТЧИК КНОПОК ==========

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик всех callback кнопок"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    print(f"🔘 Нажата кнопка: {data}")
    
    # КНОПКА НАЗАД
    if data in ["back_to_main", "back_to_start"]:
        user_id = update.effective_user.id
        
        # Получаем данные пользователя
        user_videos = db.get_user_videos(user_id)
        has_access = len(user_videos) > 0
        
        welcome_text = f"""
👋 Привет, {update.effective_user.first_name}!

🎬 Добро пожаловать в видеотеку!

{"" if has_access else "❌ У тебя пока нет доступа к видео. Приобрети подписку!"}
"""
        
        await query.edit_message_text(
            text=welcome_text,
            reply_markup=kb.get_main_menu(user_has_access=has_access),
            parse_mode="Markdown"
        )
        return
    
    # КНОПКА КУПИТЬ ДОСТУП
    elif data == "buy_access":
        await show_tariffs(update, context)
    
    # КНОПКИ ПОКУПКИ ТАРИФОВ
    elif data.startswith("buy_"):
        await buy_tariff(update, context)
    
    # КНОПКА МОИ ВИДЕО
    elif data == "my_videos":
        await show_videos_menu(update, context)
    
    # КНОПКА ПРИМЕР ВИДЕО
    elif data == "preview":
        await query.answer("🎬 Пример видео можно посмотреть после покупки", show_alert=True)
    
    # КНОПКА ПОСМОТРЕТЬ ВИДЕО
    elif data.startswith("watch_"):
        await send_video(update, context)
    
    # КНОПКА ПОМОЩЬ
    elif data == "help":
        help_text = """
🤔 **Как это работает?**

1. **Выберите тариф** — нажмите "Купить доступ"
2. **Оплатите Telegram Stars** — внутри Telegram
3. **Смотрите видео** — сразу после оплаты

⭐ **Что такое Telegram Stars?**
Это внутренняя валюта Telegram для покупок.
Пополнить звёзды можно через @PremiumBot

❓ **Проблемы с оплатой?**
Напишите в поддержку: @ваша_поддержка
"""
        await query.edit_message_text(
            text=help_text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]
            ])
        )
    
    # КНОПКА МОИ ПОДПИСКИ
    elif data == "my_subscriptions":
        await query.answer("📊 Информация о подписках скоро появится", show_alert=True)
    
    # НЕИЗВЕСТНАЯ КНОПКА
    else:
        await query.answer(f"❌ Неизвестная кнопка: {data}", show_alert=True)

# ========== ТЕСТОВАЯ КОМАНДА ==========

async def test_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):  # ИЗМЕНИЛ ИМЯ НА test_cmd
    """Тестовая команда для проверки кнопок"""
    await update.message.reply_text(
        "Тест кнопок:\n\nНажмите 'Назад'",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Тестовая кнопка Назад", callback_data="back_to_main")],
            [InlineKeyboardButton("💰 Купить доступ", callback_data="buy_access")],
            [InlineKeyboardButton("🎬 Мои видео", callback_data="my_videos")]
        ])
    )

# ========== ГЛАВНАЯ ФУНКЦИЯ ==========

print("=== DEBUG: Все функции определены, запускаем main() ===")

def main():
    print("=== DEBUG: Функция main() вызвана ===")
    """Запуск бота"""
    try:
        print("=== DEBUG: Создаем приложение ===")
        # Создаем приложение
        application = Application.builder().token(BOT_TOKEN).build()
        
        print("=== DEBUG: Добавляем обработчики команд ===")
        # Добавляем обработчики команд
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("admin_stats", admin_stats))
        application.add_handler(CommandHandler("cleanup", cleanup_command))
        
        print("=== DEBUG: Добавляем обработчики оплаты ===")
        # Обработчики оплаты
        application.add_handler(PreCheckoutQueryHandler(pre_checkout))
        application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))
        
        print("=== DEBUG: Добавляем обработчики кнопок ===")
        # Обработчики кнопок
        application.add_handler(CallbackQueryHandler(handle_callback))
        
        # Тестовая команда
        application.add_handler(CommandHandler("test", test_cmd))
        
        print("=== DEBUG: Пропускаем JobQueue для теста ===")
        # ЗАКОММЕНТИРУЙТЕ JobQueue временно
        # job_queue = application.job_queue
        # if job_queue:
        #     print("=== DEBUG: JobQueue доступен ===")
        #     # Ежедневная очистка в 3:00
        #     job_queue.run_daily(daily_cleanup, time=time(hour=3, minute=0))
        #     
        #     # Еженедельный бэкап в воскресенье в 4:00
        #     job_queue.run_repeating(backup_database, interval=604800, first=10)
        
        print("=== DEBUG: Запускаем polling ===")
        # Запускаем бота
        logger.info("🤖 Бот запущен! Для остановки нажмите Ctrl+C")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        print(f"=== DEBUG: ОШИБКА: {e} ===")
        logger.error(f"Ошибка запуска бота: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=== DEBUG: Запуск из __main__ ===")
    main()