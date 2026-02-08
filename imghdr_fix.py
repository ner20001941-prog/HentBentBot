# imghdr_fix.py
import sys

# Создаем фиктивный модуль imghdr для Python 3.14
class DummyImghdr:
    @staticmethod
    def what(file, h=None):
        return None

# Подменяем модуль
sys.modules['imghdr'] = DummyImghdr()