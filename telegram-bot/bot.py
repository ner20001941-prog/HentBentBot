#!/usr/bin/env python3
import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

BOT_TOKEN = os.getenv("BOT_TOKEN", "8554492719:AAEfcl4fTCi3WwXe4HqKilcufJDhIqMdphg")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext):
    update.message.reply_text("👋 Бот работает на PythonAnywhere!")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    
    logger.info("🤖 Бот запускается...")
    updater.start_polling()
    logger.info("✅ Бот запущен!")
    updater.idle()

if __name__ == "__main__":
    main()
