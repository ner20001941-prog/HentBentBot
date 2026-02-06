BOT_TOKEN = "8554492719:AAEfcl4fTCi3WwXe4HqKilcufJDhIqMdphg"
ADMIN_ID = 6372922355
CHANNEL_LINK = "https://t.me/+H4HYnqVsmG03ZmMy" 
CHANNEL_ID = -1003523554549

# Тарифы (продаем доступ к каналу)
TARIFFS = {
    "1_month": {
        "name": "🎬 1 месяц доступа",
        "description": "Доступ к приватному каналу на 30 дней",
        "price": 100,  # звезд
        "days": 30,
        "type": "channel_access"  # тип: доступ к каналу
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
