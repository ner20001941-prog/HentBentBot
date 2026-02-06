# create_handler.py

def add_handler_function():
    """Добавить функцию handle_callback если её нет"""
    
    with open('bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверяем есть ли уже такая функция
    if 'async def handle_callback' in content:
        print("✅ Функция handle_callback уже существует")
        return True
    
    # Ищем место куда вставить (перед def main())
    if 'def main():' in content:
        # Находим начало main()
        main_index = content.find('def main():')
        
        # Ищем последнюю функцию перед main()
        # Ищем все async def перед main
        lines = content[:main_index].split('\n')
        
        # Находим последнюю функцию
        last_func_line = -1
        for i, line in enumerate(lines):
            if 'async def ' in line or 'def ' in line:
                last_func_line = i
        
        # Вставляем после последней функции
        if last_func_line != -1:
            insert_index = sum(len(line) + 1 for line in lines[:last_func_line + 1])
            before = content[:insert_index]
            after = content[insert_index:]
        else:
            # Если функций нет, вставляем в начало после импортов
            before = content[:main_index]
            after = content[main_index:]
        
        # Код функции handle_callback
        handler_code = '''

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик всех callback кнопок"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    # КНОПКА НАЗАД
    if data in ["back_to_main", "back_to_start"]:
        await start_command(update, context)
        return
    
    # КНОПКА КУПИТЬ ДОСТУП
    elif data == "buy_access":
        await show_tariffs(update, context)
        return
    
    # КНОПКИ ПОКУПКИ ТАРИФОВ
    elif data.startswith("buy_"):
        await buy_tariff(update, context)
        return
    
    # КНОПКА МОИ ВИДЕО
    elif data == "my_videos":
        await show_user_videos_menu(update, context)
        return
    
    # КНОПКА ПОСМОТРЕТЬ ВИДЕО
    elif data.startswith("watch_"):
        await query.answer("Загружаем видео...")
        await send_video(update, context)
        return
    
    # КНОПКА ПОМОЩЬ
    elif data == "help":
        await help_command(update, context)
        return
    
    # КНОПКА МОИ ПОДПИСКИ
    elif data == "my_subscriptions":
        await query.answer("Функция в разработке", show_alert=True)
        return
    
    # КНОПКА ПРИМЕР ВИДЕО
    elif data == "preview":
        await query.answer("Пример видео скоро будет", show_alert=True)
        return
    
    # НЕИЗВЕСТНАЯ КНОПКА
    else:
        await query.answer("❌ Неизвестная команда", show_alert=True)
        return


'''
        
        new_content = before + handler_code + after
        
        with open('bot.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Функция handle_callback добавлена")
        return True
    
    print("❌ Не удалось найти def main() в файле")
    return False

def check_imports():
    """Проверить что есть все нужные импорты"""
    with open('bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверяем нужные импорты
    needed_imports = [
        'from telegram import',
        'from telegram.ext import',
        'Update',
        'ContextTypes'
    ]
    
    missing = []
    for imp in needed_imports:
        if imp not in content:
            missing.append(imp)
    
    if missing:
        print("⚠️  Возможно отсутствуют импорты:")
        for m in missing:
            print(f"   - {m}")
    
    return len(missing) == 0

if __name__ == "__main__":
    print("🛠️  Добавление функции handle_callback...")
    
    if check_imports():
        print("✅ Импорты в порядке")
    
    if add_handler_function():
        print("\n🎉 Готово! Теперь запустите бота:")
        print("python bot.py")
    else:
        print("\n❌ Не удалось добавить функцию")
        print("Добавьте вручную функцию handle_callback в bot.py")