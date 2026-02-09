import os
BOT_TOKEN = os.getenv("BOT_TOKEN", "8554492719:AAEfcl4fTCi3WwXe4HqKilcufJDhIqMdphg")
ADMIN_ID = int(os.getenv("ADMIN_ID", "6372922355"))
CHANNEL_LINK = os.getenv("CHANNEL_LINK", "https://t.me/+0CveMZwKNsVlY2Ji")
CHANNEL_ID = os.getenv("CHANNEL_ID", "-1003737348201")

# Для Railway
PORT = int(os.getenv("PORT", 8000))

# Тарифы для доступа к каналу
TARIFFS = {
    "1_day": {
        "name": "1 день доступа",
       "price": 50,

        "days": 1,
        "description": "Тестовый доступ на 1 день"
    },
    "1_week": {
        "name": "7️⃣ 1 неделя доступа",
        "price": 100,
        "days": 7,
        "description": "Доступ на 1 неделю"
    },
    "1_month": {
        "name": "📅 1 месяц доступа",
        "price": 300,
        "days": 30,
        "description": "Доступ к каналу на 1 месяц"
    },
    "forever": {
        "name": "🏆 Навсегда",
        "price": 2000,
        "days": None,
        "description": "Постоянный доступ к каналу"
    }
}
