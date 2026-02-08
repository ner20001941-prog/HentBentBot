from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from config import TARIFFS

def get_main_menu(has_access=False):
    """Главное меню бота"""
    if has_access:
        buttons = [
            [InlineKeyboardButton("🔗 Получить ссылку на канал", callback_data="get_channel_link")],
            [InlineKeyboardButton("📊 Мой доступ", callback_data="my_access")],
            [InlineKeyboardButton("💎 Купить ещё доступ", callback_data="buy_access")],
            [InlineKeyboardButton("❓ Помощь", callback_data="help")]
        ]
    else:
        buttons = [
            [InlineKeyboardButton("💎 Купить доступ за звёзды", callback_data="buy_access")],
            [InlineKeyboardButton("👁️ Предпросмотр канала", callback_data="preview")],
            [InlineKeyboardButton("❓ Как это работает?", callback_data="help")]
        ]
    
    return InlineKeyboardMarkup(buttons)

def get_tariffs_keyboard():
    """Клавиатура с выбором тарифа"""
    buttons = []
    
    for tariff_id, tariff in TARIFFS.items():
        button_text = f"{tariff['name']} - {tariff['price']} ⭐"
        buttons.append([InlineKeyboardButton(button_text, callback_data=f"buy_{tariff_id}")])
    
    buttons.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")])
    
    return InlineKeyboardMarkup(buttons)

def get_payment_keyboard(tariff_id):
    """Клавиатура для оплаты"""
    from config import TARIFFS
    tariff = TARIFFS.get(tariff_id)
    
    buttons = [
        [InlineKeyboardButton(f"💳 Оплатить {tariff['price']} ⭐", pay=True)],
        [InlineKeyboardButton("⬅️ Назад к тарифам", callback_data="buy_access")]
    ]
    
    return InlineKeyboardMarkup(buttons)