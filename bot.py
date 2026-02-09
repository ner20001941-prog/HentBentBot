#!/usr/bin/env python3
import sys
import os

# ====== ПАТЧ ДЛЯ СОВМЕСТИМОСТИ ======
# 1. Патч для urllib3
try:
    import urllib3

    sys.modules['telegram.vendor.ptb_urllib3.urllib3'] = urllib3
except:
    pass

# 2. Патч для pkg_resources (нужен APScheduler)
try:
    import pkg_resources
except ImportError:
    import types

    pkg_resources = types.ModuleType('pkg_resources')
    pkg_resources.get_distribution = lambda x: type('obj', (object,), {'version': '1.0.0'})()
    sys.modules['pkg_resources'] = pkg_resources

# 3. Патч для imghdr
try:
    import imghdr
except ImportError:
    class ImghdrStub:
        @staticmethod
        def what(file, h=None): return 'jpeg'


    sys.modules['imghdr'] = ImghdrStub()
# ====== КОНЕЦ ПАТЧА ======

import logging
from datetime import datetime
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

PORT = int(os.getenv('PORT', 8000))
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID', 0))
CHANNEL_LINK = os.getenv('CHANNEL_LINK', '')

if not BOT_TOKEN:
    print("❌ BOT_TOKEN не установлен!")
    exit(1)

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, PreCheckoutQueryHandler, MessageHandler, \
    Filters, CallbackContext

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

print("=" * 60)
print("🤖 БОТ ЗАПУСКАЕТСЯ НА RENDER")
print("=" * 60)
print(f"Python: {sys.version}")
print(f"Порт: {PORT}")
print("=" * 60)


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {"status": "ok", "service": "telegram-bot", "python": sys.version[:5]}
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass


def start_health_server():
    server = HTTPServer(('0.0.0.0', PORT), HealthHandler)
    logger.info(f"🌐 Health server на порту {PORT}")
    server.serve_forever()


def start_command(update: Update, context: CallbackContext):
    update.message.reply_text(f"👋 Бот работает на Render!\n\nКанал: {CHANNEL_LINK}")


def ping_command(update: Update, context: CallbackContext):
    update.message.reply_text("🏓 Pong! Render работает!")


def main():
    # Health сервер
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()

    # Бот
    updater = Updater(BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("ping", ping_command))
    dispatcher.add_handler(CommandHandler("help", ping_command))

    logger.info("🤖 Запускаем бота...")
    updater.start_polling()
    logger.info("✅ Бот запущен на Render!")

    updater.idle()


if __name__ == "__main__":
    main()