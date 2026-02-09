import json
import os
from datetime import datetime, timedelta

DATABASE_FILE = "user_data.json"


def init_database():
    """Инициализация базы данных"""
    if not os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=2)
        print(f"✅ Создан файл базы данных: {DATABASE_FILE}")
    else:
        print(f"✅ База данных уже существует: {DATABASE_FILE}")


def load_users():
    """Загрузить данные пользователей"""
    try:
        with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Ошибка загрузки базы данных: {e}")
        return {}


def save_users(users):
    """Сохранить данные пользователей"""
    try:
        with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ Ошибка сохранения базы данных: {e}")
        return False


def has_channel_access(user_id):
    """Проверить есть ли у пользователя доступ к каналу"""
    users = load_users()
    user_key = str(user_id)

    if user_key not in users:
        return False

    if "channel_access" not in users[user_key]:
        return False

    access_data = users[user_key]["channel_access"]
    expires_at = access_data.get("expires_at")

    if expires_at:
        try:
            expiry_date = datetime.fromisoformat(expires_at)
            return datetime.now() < expiry_date
        except:
            return True
    return True


def add_channel_access(user_id, tariff_id, days=None):
    """Добавить доступ к каналу после оплаты"""
    from config import TARIFFS

    users = load_users()
    user_key = str(user_id)

    if user_key not in users:
        users[user_key] = {
            "first_name": None,
            "username": None,
            "registered_at": datetime.now().isoformat()
        }

    tariff = TARIFFS.get(tariff_id)
    expires_at = None

    if tariff and tariff.get("days"):
        expires_at = (datetime.now() + timedelta(days=tariff["days"])).isoformat()
    elif days:  # Если days переданы отдельно
        expires_at = (datetime.now() + timedelta(days=days)).isoformat()

    users[user_key]["channel_access"] = {
        "tariff_id": tariff_id,
        "tariff_name": tariff["name"] if tariff else f"Тариф {tariff_id}",
        "price": tariff["price"] if tariff else 0,
        "granted_at": datetime.now().isoformat(),
        "expires_at": expires_at,
        "paid": True,
        "days": days or tariff.get("days") if tariff else None
    }

    # Обновляем последнюю активность
    users[user_key]["last_activity"] = datetime.now().isoformat()

    return save_users(users)


def get_user_access_info(user_id):
    """Получить информацию о доступе пользователя"""
    users = load_users()
    user_key = str(user_id)

    if user_key not in users or "channel_access" not in users[user_key]:
        return None

    return users[user_key]["channel_access"]


def register_user(user_id, first_name, username):
    """Зарегистрировать пользователя"""
    users = load_users()
    user_key = str(user_id)

    if user_key not in users:
        users[user_key] = {
            "first_name": first_name,
            "username": username,
            "registered_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat()
        }
    else:
        # Обновляем информацию
        users[user_key]["first_name"] = first_name
        users[user_key]["username"] = username
        users[user_key]["last_activity"] = datetime.now().isoformat()

    return save_users(users)


def get_all_users():
    """Получить список всех ID пользователей"""
    users = load_users()
    return [int(user_id) for user_id in users.keys()]


def get_active_users_count():
    """Получить количество пользователей с активным доступом"""
    users = load_users()
    count = 0

    for user_id, user_data in users.items():
        if has_channel_access(int(user_id)):
            count += 1

    return count


def get_stats():
    """Получить статистику бота"""
    users = load_users()
    total_users = len(users)
    active_users = get_active_users_count()

    # Считаем продажи и выручку
    total_sales = 0
    total_revenue = 0

    for user_data in users.values():
        if "channel_access" in user_data:
            total_sales += 1
            total_revenue += user_data["channel_access"].get("price", 0)

    return {
        "total_users": total_users,
        "active_users": active_users,
        "total_sales": total_sales,
        "total_revenue": total_revenue
    }


def cleanup_expired_access():
    """Очистка просроченных доступов (для CRON)"""
    users = load_users()
    cleaned_count = 0

    for user_id, user_data in users.items():
        if "channel_access" in user_data:
            expires_at = user_data["channel_access"].get("expires_at")
            if expires_at and expires_at != "forever":
                try:
                    expiry_date = datetime.fromisoformat(expires_at)
                    if datetime.now() > expiry_date:
                        # Удаляем только доступ, но оставляем пользователя
                        del user_data["channel_access"]
                        cleaned_count += 1
                except:
                    pass

    if cleaned_count > 0:
        save_users(users)

    return cleaned_count


def add_test_access(user_id, days=7):
    """Добавить тестовый доступ (для отладки)"""
    users = load_users()
    user_key = str(user_id)

    if user_key not in users:
        users[user_key] = {}

    expires_at = (datetime.now() + timedelta(days=days)).isoformat()

    users[user_key]["channel_access"] = {
        "tariff_id": "test",
        "tariff_name": "Тестовый доступ",
        "price": 0,
        "granted_at": datetime.now().isoformat(),
        "expires_at": expires_at,
        "paid": True,
        "days": days
    }

    return save_users(users)