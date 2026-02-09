#!/usr/bin/env python3
import os
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from datetime import datetime

# Настройка для Railway
PORT = int(os.getenv('PORT', 8000))
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID', 0))
CHANNEL_LINK = os.getenv('CHANNEL_LINK', '-1003523554549')

# Импорт telegram
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

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# Health check сервер
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {"status": "ok", "bot": "running"}
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()


def start_health_server():
    server = HTTPServer(('0.0.0.0', PORT), HealthHandler)
    server.serve_forever()


# Команда /start
def start_command(update: Update, context: CallbackContext):
    update.message.reply_text(
        f"👋 Привет! Бот работает на Railway!\n\nКанал: {CHANNEL_LINK}",
        parse_mode="HTML"
    )


def main():
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN не установлен!")
        return

    # Запускаем health сервер
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()

    # Создаем бота
    updater = Updater(BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Регистрируем команды
    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("ping",
                                          lambda u, c: u.message.reply_text("🏓 Pong!")))

    # Запускаем
    logger.info(f"🤖 Бот запускается на порту {PORT}")
    updater.start_polling()
    logger.info("✅ Бот запущен!")

    updater.idle()


if __name__ == "__main__":
    main()