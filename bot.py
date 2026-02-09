#!/usr/bin/env python3
import sys
import os

# ====== ПАТЧ ДЛЯ СОВМЕСТИМОСТИ ======
try:
    import urllib3
    sys.modules['telegram.vendor.ptb_urllib3.urllib3'] = urllib3
except:
    pass

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

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "service": "telegram-bot"}).encode())
        else:
            self.send_response(404)
            self.end_headers()

def start_health_server():
    server = HTTPServer(('0.0.0.0', PORT), HealthHandler)
    server.serve_forever()

def start_command(update: Update, context: CallbackContext):
    update.message.reply_text(f"👋 Бот работает на Render!\n\nКанал: {CHANNEL_LINK}")

def main():
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()
    
    updater = Updater(BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    
    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("ping", lambda u,c: u.message.reply_text("🏓 Pong!")))
    
    logger.info("🤖 Бот запускается...")
    updater.start_polling()
    logger.info("✅ Бот запущен!")
    updater.idle()

if __name__ == "__main__":
    main()
