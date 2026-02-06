# test_simple.py
import sys
import os

# Фикс для Windows
if sys.platform == 'win32':
    sys.stderr = open(os.devnull, 'w')

import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = "ВАШ_ТОКЕН_БОТА"  # Замените на реальный токен

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Простой бот работает!")

def main():
    print("Запускаем простого бота...")
    
    try:
        app = Application.builder().token(BOT_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        
        print("🤖 Простой бот запущен!")
        app.run_polling()
        
    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()