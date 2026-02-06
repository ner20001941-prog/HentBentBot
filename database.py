import json
import time
from datetime import datetime, timedelta
from config import TARIFFS

def init_database():
    """Инициализация базы данных"""
    try:
        with open("user_data.json", "r", encoding="utf-8") as f:
            pass
    except FileNotFoundError:
        with open("user_data.json", "w", encoding="utf-8") as f:
            json.dump({}, f)

def load_users():
    """Загрузить данные пользователей"""
    try:
        with open("user_data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    """Сохранить данные пользователей"""
    with open("user_data.json", "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def add_channel_access(user_id, tariff_id):
    """Добавить доступ к каналу"""
    users = load_users()
    user_key = str(user_id)
    
    if user_key not in users:
        users[user_key] = {"channel_access": {}}
    
    tariff = TARIFFS.get(tariff_id, {})
    days = tariff.get("days")
    
    # Определяем срок истечения
    if days is None:
        expires_at = None  # Бессрочный доступ
    else:
        expires_at = (datetime.now() + timedelta(days=days)).isoformat()
    
    users[user_key]["channel_access"] = {
        "tariff_id": tariff_id,
        "purchased_at": datetime.now().isoformat(),
        "expires_at": expires_at
    }
    
    save_users(users)
    return True

def has_channel_access(user_id):
    """Проверить есть ли доступ к каналу"""
    users = load_users()
    user_data = users.get(str(user_id), {})
    
    if "channel_access" not in user_data:
        return False
    
    access_data = user_data["channel_access"]
    
    # Проверяем срок действия
    expires_at = access_data.get("expires_at")
    if expires_at is None:
        return True  # Бессрочный доступ
    
    try:
        expiry_date = datetime.fromisoformat(expires_at)
        return datetime.now() < expiry_date
    except:
        return False

def get_access_expiry(user_id):
    """Получить информацию о сроке доступа"""
    users = load_users()
    user_data = users.get(str(user_id), {})
    
    if "channel_access" not in user_data:
        return "Нет доступа"
    
    access_data = user_data["channel_access"]
    expires_at = access_data.get("expires_at")
    
    if expires_at is None:
        return "Бессрочный доступ"
    
    try:
        expiry_date = datetime.fromisoformat(expires_at)
        days_left = (expiry_date - datetime.now()).days
        
        if days_left < 0:
            return "Доступ истек"
        elif days_left == 0:
            return "Доступ истекает сегодня"
        else:
            return f"Доступно еще {days_left} дней"
    except:
        return "Ошибка проверки срока"

def cleanup_expired():
    """Очистка истекших подписок"""
    users = load_users()
    cleaned_count = 0
    
    for user_key, user_data in list(users.items()):
        if "channel_access" in user_data:
            access_data = user_data["channel_access"]
            expires_at = access_data.get("expires_at")
            
            if expires_at:
                try:
                    expiry_date = datetime.fromisoformat(expires_at)
                    if datetime.now() > expiry_date:
                        # Удаляем истекший доступ
                        del users[user_key]["channel_access"]
                        cleaned_count += 1
                except:
                    pass
    
    if cleaned_count > 0:
        save_users(users)
    
    return cleaned_count

# ========== СТАРЫЕ ФУНКЦИИ (УДАЛИТЕ ИХ) ==========
# Удалите эти функции если они есть:

def get_user_videos(user_id):
    """Получить все видео, доступные пользователю (СТАРАЯ ФУНКЦИЯ - НЕ НУЖНА)"""
    return []  # Возвращаем пустой список

def add_subscription(user_id, tariff_id):
    """Добавить подписку пользователю (СТАРАЯ ФУНКЦИЯ - НЕ НУЖНА)"""
    # Используем новую функцию для доступа к каналу
    return add_channel_access(user_id, tariff_id)

def is_subscription_expired(subscription_data):
    """Проверить истекла ли подписка (СТАРАЯ ФУНКЦИЯ - НЕ НУЖНА)"""
    return False

def get_expiration_date(tariff_id):
    """Получить дату истечения подписки (СТАРАЯ ФУНКЦИЯ - НЕ НУЖНА)"""
    return None
def get_expired_users():
    """Получить список пользователей с истекшей подпиской"""
    users = load_users()
    expired_users = []
    
    for user_key, user_data in users.items():
        if "channel_access" in user_data:
            access_data = user_data["channel_access"]
            expires_at = access_data.get("expires_at")
            
            if expires_at:
                try:
                    expiry_date = datetime.fromisoformat(expires_at)
                    if datetime.now() > expiry_date:
                        expired_users.append({
                            "user_id": int(user_key),
                            "tariff_id": access_data.get("tariff_id"),
                            "expired_at": expires_at
                        })
                except:
                    pass
    
    return expired_users

def revoke_access(user_id):
    """Отозвать доступ пользователя"""
    users = load_users()
    user_key = str(user_id)
    
    if user_key in users and "channel_access" in users[user_key]:
        del users[user_key]["channel_access"]
        save_users(users)
        return True
    
    return False