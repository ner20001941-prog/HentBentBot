#!/usr/bin/env python3
"""
Скрипт для загрузки видео в систему
"""

import os
import sys
import json
from config import VIDEOS, PATHS
from database import db

def upload_videos():
    """Загрузить видео из конфига в базу данных"""
    print("📤 Загрузка видео в базу данных...")
    
    uploaded = 0
    for video_id, video_info in VIDEOS.items():
        # Проверяем существует ли видео
        if not os.path.exists(video_info['file_path']):
            print(f"⚠️  Файл не найден: {video_info['file_path']}")
            
            # Создаем заглушку для тестирования
            os.makedirs(os.path.dirname(video_info['file_path']), exist_ok=True)
            with open(video_info['file_path'], 'w') as f:
                f.write(f"Это заглушка для {video_info['title']}")
            print(f"📝 Создана заглушка: {video_info['file_path']}")
        
        # Добавляем видео в базу
        video_db_id = db.add_video(
            title=video_info['title'],
            description=video_info['description'],
            category=video_info['category'],
            tags=video_info['tags'],
            file_path=video_info['file_path'],
            price=video_info['price'],
            is_free=video_info['is_free'],
            duration=video_info.get('duration')
        )
        
        if video_db_id:
            print(f"✅ {video_info['title']} добавлено (ID: {video_db_id})")
            uploaded += 1
        else:
            print(f"❌ Ошибка добавления: {video_info['title']}")
    
    print(f"\n🎉 Загружено {uploaded} из {len(VIDEOS)} видео")
    return uploaded

def check_video_files():
    """Проверить существование видео файлов"""
    print("🔍 Проверка видео файлов...")
    
    missing = []
    for video_id, video_info in VIDEOS.items():
        if os.path.exists(video_info['file_path']):
            size_mb = os.path.getsize(video_info['file_path']) / (1024 * 1024)
            print(f"✅ {video_info['title']}: {size_mb:.1f} MB")
        else:
            print(f"❌ {video_info['title']}: ФАЙЛ ОТСУТСТВУЕТ")
            missing.append(video_info['file_path'])
    
    return missing

def create_sample_videos():
    """Создать тестовые видео файлы"""
    print("🎬 Создание тестовых видео файлов...")
    
    for video_id, video_info in VIDEOS.items():
        video_path = video_info['file_path']
        video_dir = os.path.dirname(video_path)
        
        # Создаем директорию если нужно
        os.makedirs(video_dir, exist_ok=True)
        
        # Создаем текстовый файл как заглушку
        with open(video_path, 'w') as f:
            content = f"""
            Видео: {video_info['title']}
            Описание: {video_info['description']}
            Длительность: {video_info.get('duration', 0)} секунд
            Категория: {video_info['category']}
            
            Это тестовый файл. В продакшене здесь должно быть реальное видео.
            """
            f.write(content)
        
        print(f"📝 Создана заглушка: {video_info['title']}")
    
    print("✅ Все тестовые файлы созданы")

if __name__ == "__main__":
    print("=" * 50)
    print("       🎬 СИСТЕМА ЗАГРУЗКИ ВИДЕО")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "check":
            missing = check_video_files()
            if missing:
                print(f"\n⚠️  Отсутствует {len(missing)} файлов")
                print("Запустите: python upload_videos.py create")
        elif command == "create":
            create_sample_videos()
        elif command == "upload":
            upload_videos()
        else:
            print(f"Неизвестная команда: {command}")
    else:
        # Интерактивный режим
        print("\nВыберите действие:")
        print("1. Проверить видео файлы")
        print("2. Создать тестовые файлы")
        print("3. Загрузить видео в базу")
        print("4. Сделать всё")
        
        choice = input("\nВведите номер: ").strip()
        
        if choice == "1":
            check_video_files()
        elif choice == "2":
            create_sample_videos()
        elif choice == "3":
            upload_videos()
        elif choice == "4":
            print("\n🔍 Проверка файлов...")
            check_video_files()
            print("\n🎬 Создание файлов...")
            create_sample_videos()
            print("\n📤 Загрузка в базу...")
            upload_videos()
            print("\n✅ Все операции завершены!")
        else:
            print("❌ Неверный выбор")