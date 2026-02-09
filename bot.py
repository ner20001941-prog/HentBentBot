#!/usr/bin/env python3
import sys
import os

# ====== ПАТЧ ДЛЯ PYTHON 3.13+ ======
# 1. Патч для pkg_resources (если нет в Python 3.13+)
try:
    import pkg_resources
except ImportError:
    # Создаем фиктивный модуль
    class FakeDistribution:
        def __init__(self, version='1.0.0'):
            self.version = version


    def get_distribution(name):
        return FakeDistribution('1.0.0')


    class DistributionNotFound(Exception):
        pass


    pkg_resources_module = type(sys)('pkg_resources')
    pkg_resources_module.get_distribution = get_distribution
    pkg_resources_module.DistributionNotFound = DistributionNotFound
    sys.modules['pkg_resources'] = pkg_resources_module
    print("✅ Создан фиктивный pkg_resources")

# 2. Патч для urllib3
try:
    import urllib3

    sys.modules['telegram.vendor.ptb_urllib3.urllib3'] = urllib3
    print("✅ Патч urllib3 применен")
except ImportError:
    print("❌ urllib3 не установлен")

# 3. Патч для imghdr
try:
    import imghdr
except ImportError:
    class ImghdrStub:
        @staticmethod
        def what(file, h=None):
            return 'jpeg'


    sys.modules['imghdr'] = ImghdrStub()
    print("✅ Патч imghdr применен")
# ====== КОНЕЦ ПАТЧА ======

import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    print("❌ BOT_TOKEN не установлен!")
    sys.exit(1)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext):
    update.message.reply_text("✅ Бот работает на Render!")


def ping(update: Update, context: CallbackContext):
    update.message.reply_text("🏓 Pong!")


def main():
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