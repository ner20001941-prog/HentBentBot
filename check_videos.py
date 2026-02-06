import os
import sys

# Добавляем путь к config.py
sys.path.append('.')

from config import VIDEOS

print("=" * 70)
print("ПРОВЕРКА ВИДЕО ФАЙЛОВ")
print("=" * 70)

current_dir = os.getcwd()
print(f"Текущая директория: {current_dir}")
print()

for video_id, info in VIDEOS.items():
    print(f"Видео: {info['title']}")
    print(f"  ID: {video_id}")
    print(f"  Путь в конфиге: {info['file_path']}")
    
    file_path = info['file_path']
    
    # 1. Проверяем существование файла
    exists = os.path.exists(file_path)
    print(f"  Файл существует: {'✅' if exists else '❌'}")
    
    if exists:
        # 2. Проверяем размер
        size = os.path.getsize(file_path)
        size_mb = size / (1024 * 1024)
        print(f"  Размер: {size_mb:.2f} MB")
        
        # 3. Проверяем читаемость
        readable = os.access(file_path, os.R_OK)
        print(f"  Доступен для чтения: {'✅' if readable else '❌'}")
        
        # 4. Проверяем расширение
        extension = os.path.splitext(file_path)[1].lower()
        print(f"  Расширение: {extension}")
        
        # 5. Проверяем лимит Telegram
        if size_mb > 50:
            print(f"  ⚠️  ПРЕДУПРЕЖДЕНИЕ: Файл больше 50MB ({size_mb:.2f} MB)")
    else:
        print(f"  🔍 Поиск файла...")
        # Ищем файл в разных местах
        possible_paths = [
            file_path,
            os.path.join(current_dir, file_path),
            os.path.join(current_dir, 'videos', os.path.basename(file_path)),
            os.path.join('videos', os.path.basename(file_path))
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                print(f"  ✅ Найден по альтернативному пути: {path}")
                break
    
    print()