# check_env.py
from dotenv import load_dotenv
import os

load_dotenv()

token = os.getenv('BOT_TOKEN')
admin_id = os.getenv('ADMIN_ID')

print(f"Токен: {token}")
print(f"Админ ID: {admin_id}")