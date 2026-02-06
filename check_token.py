# check_token.py
import requests

# Возможный правильный токен
possible_token = "8554492719:AAEfcl4fTCi3WwXe4HqKilcufJDhIqMdphg"

def check_token(token):
    url = f"https://api.telegram.org/bot{token}/getMe"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True, "✓ Токен правильный!"
        else:
            return False, f"✗ Токен неправильный. Код: {response.status_code}"
    except Exception as e:
        return False, f"✗ Ошибка: {e}"

print("Проверка токенов...")
print(f"1. Текущий: {wrong_token}")
ok, msg = check_token(wrong_token)
print(f"   {msg}")

print(f"\n2. Возможный правильный: {possible_token}")
ok, msg = check_token(possible_token)
print(f"   {msg}")

print("\nКак получить правильный токен:")
print("1. Откройте Telegram")
print("2. Найдите @BotFather")
print("3. Напишите /mybots")
print("4. Выберите вашего бота")
print("5. Нажмите 'API Token'")
print("6. Скопируйте токен")