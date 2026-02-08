@echo off
echo ====================================
echo Установка Telegram бота с Python 3.11
echo ====================================

echo 1. Проверяем Python...
python --version

echo 2. Создаем/очищаем venv...
if exist venv rmdir /s /q venv
python -m venv venv

echo 3. Активируем venv...
call venv\Scripts\activate.bat

echo 4. Обновляем pip...
python -m pip install --upgrade pip

echo 5. Устанавливаем зависимости...
pip install "python-telegram-bot[job-queue]==13.15"

echo 6. Проверяем установку...
python -c "import telegram; print('✅ telegram установлен')"

echo.
echo ====================================
echo Установка завершена!
echo Запустите бота: python bot.py
echo ====================================
pause