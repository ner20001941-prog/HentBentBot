from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import TARIFFS, CHANNEL_LINK

def get_main_menu(has_access=False):
    """Главное меню для доступа к каналу"""
    buttons = []
    
    if has_access:
        buttons.append([InlineKeyboardButton("🔗 Получить ссылку на канал", callback_data="get_channel_link")])
        buttons.append([InlineKeyboardButton("📊 Мой доступ", callback_data="my_access")])
    
    buttons.append([InlineKeyboardButton("💰 Купить доступ", callback_data="buy_access")])
    buttons.append([InlineKeyboardButton("👁️‍🗨️ Предпросмотр", callback_data="preview")])
    buttons.append([InlineKeyboardButton("❓ Помощь", callback_data="help")])
    
    return InlineKeyboardMarkup(buttons)

def get_tariffs_keyboard():
    """Клавиатура с тарифами для канала"""
    buttons = []
    
    for tariff_id, tariff_info in TARIFFS.items():
        button_text = f"{tariff_info['name']} - {tariff_info['price']} ⭐"
        buttons.append([InlineKeyboardButton(button_text, callback_data=f"buy_{tariff_id}")])
    
    buttons.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")])
    
    return InlineKeyboardMarkup(buttons)