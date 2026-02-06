# auto_fix.py
import sys

print("🔧 Автоматическое исправление ошибки handle_callback...")

# Читаем bot.py
with open('bot.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Ищем def main()
main_line = -1
for i, line in enumerate(lines):
    if 'def main():' in line:
        main_line = i
        break

if main_line == -1:
    print("❌ Не найден def main()")
    sys.exit(1)

# Проверяем есть ли handle_callback
has_handler = False
for line in lines:
    if 'async def handle_callback' in line:
        has_handler = True
        break

if not has_handler:
    # Добавляем функцию перед main
    handler_code = [
        '\n',
        'async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):\n',
        '    """Обработчик всех callback кнопок"""\n',
        '    query = update.callback_query\n',
        '    await query.answer()\n',
        '    \n',
        '    data = query.data\n',
        '    \n',
        '    if data == "back_to_main":\n',
        '        await start_command(update, context)\n',
        '    elif data == "buy_access":\n',
        '        await show_tariffs(update, context)\n',
        '    elif data.startswith("buy_"):\n',
        '        await buy_tariff(update, context)\n',
        '    elif data == "my_videos":\n',
        '        await show_user_videos_menu(update, context)\n',
        '    elif data.startswith("watch_"):\n',
        '        await send_video(update, context)\n',
        '    elif data == "help":\n',
        '        await help_command(update, context)\n',
        '    else:\n',
        '        await query.answer("❌ Неизвестная команда")\n',
        '\n'
    ]
    
    # Вставляем перед main
    lines = lines[:main_line] + handler_code + lines[main_line:]
    
    print("✅ Функция handle_callback добавлена")

# Записываем обратно
with open('bot.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("🎉 Файл исправлен! Запускайте бота:")
print("python bot.py")