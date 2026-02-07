import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
CHANNEL_LINK = os.getenv("CHANNEL_LINK", "")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))

TARIFFS = {
    "1_month": {
        "name": "🎬 1 месяц доступа",
        "description": "Доступ к приватному каналу на 30 дней",
        "price": 100,
        "days": 30,
        "type": "channel_access"
    },
    "3_months": {
        "name": "🔥 3 месяца доступа",
        "description": "Доступ к приватному каналу на 90 дней",
        "price": 250,
        "days": 90,
        "type": "channel_access"
    },
    "forever": {
        "name": "👑 Навсегда",
        "description": "Пожизненный доступ к приватному каналу",
        "price": 500,
        "days": None,
        "type": "channel_access"
    }
}

print(f"✅ Конфигурация загружена")
print(f"   Бот токен: {BOT_TOKEN[:10]}...")
print(f"   Админ ID: {ADMIN_ID}")
print(f"   Канал: {CHANNEL_LINK}")
