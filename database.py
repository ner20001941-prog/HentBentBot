import json
import os
from datetime import datetime, timedelta

DATABASE_FILE = "user_data.json"

def init_database():
    """Инициализация базы данных"""
    if not os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=2)

def load_users():
    """Загрузить данные пользователей"""
    try:
        with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    """Сохранить данные пользователей"""
    with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

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

def add_channel_access(user_id, tariff_id):
    """Добавить доступ к каналу после оплаты"""
    from config import TARIFFS
    
    users = load_users()
    user_key = str(user_id)
    
    if user_key not in users:
        users[user_key] = {}
    
    tariff = TARIFFS.get(tariff_id)
    expires_at = None
    
    if tariff and tariff.get("days"):
        expires_at = (datetime.now() + timedelta(days=tariff["days"])).isoformat()
    
    users[user_key]["channel_access"] = {
        "tariff_id": tariff_id,
        "granted_at": datetime.now().isoformat(),
        "expires_at": expires_at,
        "paid": True
    }
    
    save_users(users)
    return True

def get_user_access_info(user_id):
    """Получить информацию о доступе пользователя"""
    users = load_users()
    user_key = str(user_id)
    
    if user_key not in users or "channel_access" not in users[user_key]:
        return None
    
    return users[user_key]["channel_access"]

def get_active_users_count():
    """Получить количество пользователей с активным доступом"""
    users = load_users()
    count = 0
    
    for user_data in users.values():
        if has_channel_access(int(list(users.keys())[0])):
            count += 1
    
    return count