# debug_buttons.py
from telegram import Update
from telegram.ext import Application, CallbackQueryHandler, ContextTypes
import asyncio

async def debug_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    print(f"🔍 DEBUG: callback_data = '{query.data}'")
    print(f"🔍 DEBUG: message_id = {query.message.message_id}")
    print(f"🔍 DEBUG: chat_id = {query.message.chat.id}")
    await query.answer(f"Нажата кнопка: {query.data}")

async def main():
    # Временный токен для теста
    app = Application.builder().token("DUMMY_TOKEN").build()
    app.add_handler(CallbackQueryHandler(debug_callback))
    
    print("Тестовый обработчик создан")
    print("Запустите бота и нажмите кнопку 'Назад'")
    print("В консоли появится callback_data этой кнопки")

if __name__ == "__main__":
    asyncio.run(main())