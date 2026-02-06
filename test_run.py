import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from config import BOT_TOKEN, CHANNEL_LINK

async def simple_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Простейший тест"""
    await update.message.reply_text(
        f"🔗 ССЫЛКА:\n{CHANNEL_LINK}",
        disable_web_page_preview=False
    )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("test", simple_test))
    
    print("✅ Тестовый бот запущен! Отправьте /test")
    app.run_polling()

if __name__ == "__main__":
    main()