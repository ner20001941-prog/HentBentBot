import sys
print("✅ Python работает!")
print(f"Версия Python: {sys.version}")
print(f"Путь: {sys.executable}")

try:
    import telegram
    print("✅ Библиотека telegram установлена")
except ImportError as e:
    print(f"❌ Ошибка импорта telegram: {e}")