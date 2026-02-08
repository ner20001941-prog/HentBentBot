@echo off
echo Запуск отладки бота...
python --version
echo.
echo Проверка импортов...
python -c "import telegram; print('✅ Библиотека telegram установлена')"
echo.
echo Запуск бота...
python bot.py
echo.
echo Бот завершился с кодом: %errorlevel%
pause