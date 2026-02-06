# debug_full.py
import sys
import os
import traceback

print("=== НАЧАЛО ОТЛАДКИ ===")

# Фикс для Windows
if sys.platform == 'win32':
    sys.stderr = open(os.devnull, 'w')

try:
    print("1. Проверяем базовые импорты...")
    import asyncio
    from datetime import datetime, time, timedelta
    import logging
    print("   ✓ Базовые импорты OK")
    
    print("2. Проверяем telegram импорты...")
    from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update, LabeledPrice
    from telegram.ext import (
        Application,
        CommandHandler,
        CallbackQueryHandler,
        PreCheckoutQueryHandler,
        MessageHandler,
        filters,
        ContextTypes,
        JobQueue
    )
    print("   ✓ Telegram импорты OK")
    
    print("3. Проверяем config.py...")
    from config import BOT_TOKEN, TARIFFS, VIDEOS, ADMIN_ID
    print(f"   ✓ Токен: {BOT_TOKEN[:15]}...")
    print(f"   ✓ Тарифов: {len(TARIFFS)}")
    print(f"   ✓ Видео: {len(VIDEOS)}")
    print(f"   ✓ Админ ID: {ADMIN_ID}")
    
    print("4. Проверяем database.py...")
    import database as db
    print("   ✓ database.py OK")
    
    print("5. Проверяем keyboards.py...")
    import keyboards as kb
    print("   ✓ keyboards.py OK")
    
    print("6. Импортируем функции из bot.py...")
    # Импортируем нужные функции из bot.py
    from bot import (
        start_command,
        help_command,
        show_tariffs,
        buy_tariff,
        pre_checkout,
        successful_payment,
        show_videos_menu,
        send_video,
        admin_stats,
        cleanup_command,
        handle_callback,
        test_cmd,
        main
    )
    print("   ✓ Все функции импортированы")
    
    print("\n=== ЗАПУСКАЕМ БОТА ===")
    main()
    
except KeyboardInterrupt:
    print("\n✓ Бот остановлен пользователем")
except Exception as e:
    print(f"\n✗ ОШИБКА: {e}")
    traceback.print_exc()
    print("\nПроверьте:")
    print("1. Токен бота в .env файле")
    print("2. Файлы database.py, keyboards.py в той же папке")
    print("3. Версию python-telegram-bot: pip show python-telegram-bot")

input("\nНажмите Enter для выхода...")