# imghdr.py - заглушка для Python 3.14+
"""Заглушка для удаленного модуля imghdr в Python 3.14+"""


def what(file, h=None):
    """
    Определяет тип изображения.
    Возвращает 'jpeg', 'png', 'gif', 'bmp' или None.
    """
    # Простая реализация для работы python-telegram-bot
    if hasattr(file, 'name'):
        filename = file.name.lower()
    elif isinstance(file, str):
        filename = file.lower()
    else:
        return None

    if filename.endswith(('.jpg', '.jpeg')):
        return 'jpeg'
    elif filename.endswith('.png'):
        return 'png'
    elif filename.endswith('.gif'):
        return 'gif'
    elif filename.endswith('.bmp'):
        return 'bmp'
    elif filename.endswith('.tiff') or filename.endswith('.tif'):
        return 'tiff'
    return None


def test():
    """Тестовая функция"""
    pass


# Для обратной совместимости
def test_jpeg():
    pass


def test_png():
    pass


def test_gif():
    pass


def test_bmp():
    pass


def test_tiff():
    pass