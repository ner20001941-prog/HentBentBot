# Патч для совместимости
import fix_imports

# Патч для импортов
try:
    import fix_imports
except:
    pass

#!/usr/bin/env python3

# Патч для импортов
try:
    import fix_imports
except:
    pass

import os
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from datetime import datetime

# Для telegram bot версии 20.x
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    PreCheckoutQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)

# Настройка для Railway
PORT = int(os.environ.get('PORT', 8000))
BOT_TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = int(os.environ.get('ADMIN_ID', 0))
CHANNEL_LINK = os.environ.get('CHANNEL_LINK', '')

# Проверка токена
if not BOT_TOKEN:
    print("❌ ОШИБКА: BOT_TOKEN не установлен!")
    print("Установите переменную окружения BOT_TOKEN")
    exit(1)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

print("=" * 60)
print("🤖 БОТ ДЛЯ Railway (Telegram Bot v20.x)")
print("=" * 60)
print(f"Порт: {PORT}")
print(f"Токен: {BOT_TOKEN[:10]}...")
print("=" * 60)
try:
    import imghdr
except ImportError:
    # Создаем простую заглушку
    import sys
    import os


    class ImghdrStub:
        @staticmethod
        def what(file, h=None):
            # Простая реализация для работы telegram-bot
            if hasattr(file, 'name'):
                name = file.name.lower()
            elif isinstance(file, str):
                name = file.lower()
            else:
                return None

            if name.endswith(('.jpg', '.jpeg')):
                return 'jpeg'
            elif name.endswith('.png'):
                return 'png'
            elif name.endswith('.gif'):
                return 'gif'
            elif name.endswith('.bmp'):
                return 'bmp'
            elif name.endswith(('.tiff', '.tif')):
                return 'tiff'
            return None


    sys.modules['imghdr'] = ImghdrStub()
    print("⚠️ Используется заглушка imghdr для Python 3.14")

# === КОНЕЦ ПАТЧА ===

import sys
import os
import logging


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

    def log_message(self, format, *args):
        pass


def start_health_server():
    server = HTTPServer(('0.0.0.0', PORT), HealthHandler)
    logger.info(f"🌐 Health server на порту {PORT}")
    server.serve_forever()


# Команды
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"👋 Бот работает! Канал: {CHANNEL_LINK}")


async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 Pong!")


def main():
    # Запускаем health сервер
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()

    # Создаем Application (вместо Updater в v20.x)
    application = Application.builder().token(BOT_TOKEN).build()

    # Регистрируем команды
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("ping", ping_command))

    print("✅ Бот запускается...")

    # Запускаем polling
    application.run_polling(allowed_updates=Update.ALL_TYPES)

    print("✅ Бот запущен!")


if __name__ == "__main__":
    main()