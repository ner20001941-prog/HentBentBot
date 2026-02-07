import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Конфигурация
BOT_TOKEN = os.getenv("BOT_TOKEN", "8554492719:AAEfcl4fTCi3WwXe4HqKilcufJDhIqMdphg")
ADMIN_ID = 6372922355
CHANNEL_LINK = "https://t.me/+H4HYnqVsmG03ZmMy"

# Настройка логов
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Бот работает на Railway!")

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 Pong! Бот активен!")

def main():
    print("🚀 Запуск бота на Railway...")
    
    try:
        # ТОЛЬКО Application
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Добавляем обработчики
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("ping", ping))
        
        print("✅ Бот сконфигурирован")
        print("=" * 50)
        print(" Бот запущен успешно!")
        print("=" * 50)
        
        # ЗАПУСКАЕМ
        application.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        )
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()