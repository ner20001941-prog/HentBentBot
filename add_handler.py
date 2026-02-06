# add_handler.py
import os

def add_handler_function():
    """Добавить функцию handle_callback в bot.py"""
    
    with open('bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Если функция уже есть - выходим
    if 'async def handle_callback' in content:
        print("✅ Функция handle_callback уже существует")
        return True
    
    # Находим где вставить (перед def main)
    main_index = content.find('def main():')
    if main_index == -1:
        print("❌ Не найден def main()")
        return False
    
    # Вставляем функцию перед main
    before_main = content[:main_index]
    after_main = content[main_index:]
    
    handler_code = '''
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик всех callback кнопок"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    print(f"🔘 Кнопка: {data}")
    
    # КНОПКА НАЗАД
    if data in ["back_to_main", "back_to_start", "back"]:
        await start_command(update, context)
    
    # КНОПКА КУПИТЬ ДОСТУП
    elif data == "buy_access":
        await show_tariffs(update, context)
    
    # КНОПКИ ПОКУПКИ
    elif data.startswith("buy_"):
        await buy_tariff(update, context)
    
    # КНОПКА МОИ ВИДЕО
    elif data == "my_videos":
        await show_user_videos_menu(update, context)
    
    # КНОПКА ПОСМОТРЕТЬ ВИДЕО
    elif data.startswith("watch_"):
        await query.answer("🎬 Загружаем видео...")
        await send_video(update, context)
    
    # КНОПКА ПОМОЩЬ
    elif data == "help":
        await help_command(update, context)
    
    # ДРУГИЕ КНОПКИ
    elif data == "my_subscriptions":
        await query.answer("📊 Загружаем информацию...")
        # Добавьте свою функцию или удалите эту строку
        await query.edit_message_text("Функция в разработке")
    
    elif data == "preview":
        await query.answer("Пример видео")
        try:
            await context.bot.send_video(
                chat_id=update.effective_chat.id,
                video=open('videos/vid_360p.mp4', 'rb'),
                caption="Пример видео (бесплатно)"
            )
        except:
            await query.edit_message_text("Пример видео: vid_360p.mp4")
    
    # НЕИЗВЕСТНАЯ КНОПКА
    else:
        await query.answer(f"❌ Неизвестно: {data}", show_alert=True)

'''
    
    new_content = before_main + handler_code + after_main
    
    with open('bot.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Функция handle_callback добавлена!")
    return True

if __name__ == "__main__":
    print("🛠️ Добавляю функцию handle_callback...")
    if add_handler_function():
        print("\n🎉 Готово! Теперь запустите бота:")
        print("python bot.py")
    else:
        print("\n❌ Не удалось добавить функцию")