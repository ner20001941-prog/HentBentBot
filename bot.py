#!/usr/bin/env python3
import sys
import os

# ====== КРИТИЧЕСКИЙ ПАТЧ ДЛЯ RENDER ======
# ДО ЛЮБЫХ ИМПОРТОВ TELEGRAM!

# 1. Устанавливаем urllib3 в sys.modules перед импортом telegram
try:
    import urllib3

    # Создаем полный путь для vendor
    sys.modules['telegram.vendor.ptb_urllib3'] = type(sys)('ptb_urllib3')
    sys.modules['telegram.vendor.ptb_urllib3'].urllib3 = urllib3
    sys.modules['telegram.vendor.ptb_urllib3.urllib3'] = urllib3

    # Создаем packages.six.moves структуру
    import six


    class FakePackages:
        class six:
            moves = six.moves


    fake_packages = FakePackages()
    sys.modules['telegram.vendor.ptb_urllib3.urllib3.packages'] = fake_packages
    sys.modules['telegram.vendor.ptb_urllib3.urllib3.packages.six'] = fake_packages.six

    print("✅ Патч urllib3 применен")
except ImportError as e:
    print(f"❌ Ошибка urllib3: {e}")
    sys.exit(1)
except Exception as e:
    print(f"⚠️ Предупреждение патча: {e}")

# 2. Патч для imghdr
try:
    import imghdr
except ImportError:
    class ImghdrStub:
        @staticmethod
        def what(file, h=None):
            return 'jpeg'


    sys.modules['imghdr'] = ImghdrStub()
    print("✅ Патч imghdr применен")

# 3. Патч для six.moves
try:
    import six

    if not hasattr(six, 'moves'):
        class Moves:
            class http_client:
                IncompleteRead = Exception


        six.moves = Moves()


    # Создаем фиктивный модуль для telegram.vendor.ptb_urllib3.urllib3.packages
    class FakePackages:
        class six:
            moves = six.moves


    fake_packages = FakePackages()
    sys.modules['telegram.vendor.ptb_urllib3.urllib3.packages'] = fake_packages
    sys.modules['telegram.vendor.ptb_urllib3.urllib3.packages.six'] = fake_packages.six
    print("✅ six.moves патч применен")
except Exception as e:
    print(f"⚠️ six патч не применен: {e}")
# ====== КОНЕЦ ПАТЧА ======

import logging
from datetime import datetime
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

PORT = int(os.getenv('PORT', 8000))
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    print("❌ BOT_TOKEN не установлен!")
    sys.exit(1)

# Только ПОСЛЕ патчей импортируем telegram
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

print("=" * 60)
print("🤖 БОТ ЗАПУСКАЕТСЯ")
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


def start(update: Update, context: CallbackContext):
    update.message.reply_text("✅ Бот работает на Render!")


def ping(update: Update, context: CallbackContext):
    update.message.reply_text("🏓 Pong!")


def main():
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()

    updater = Updater(BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("ping", ping))

    logger.info("🤖 Запуск бота...")
    updater.start_polling()
    logger.info("✅ Бот запущен!")
    updater.idle()


if __name__ == "__main__":
    main()