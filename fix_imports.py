import sys
import os

# Патч для совместимости python-telegram-bot на Python 3.13+
try:
    import urllib3
    # Создаем фиктивный модуль для обхода ошибки
    sys.modules['telegram.vendor.ptb_urllib3.urllib3'] = urllib3
    print("✅ Применен патч для urllib3")
    
    # Патч для imghdr (удален в Python 3.13+)
    try:
        import imghdr
    except ImportError:
        class ImghdrStub:
            @staticmethod
            def what(file, h=None):
                return 'jpeg'
        sys.modules['imghdr'] = ImghdrStub()
        print("✅ Применен патч для imghdr")
        
except Exception as e:
    print(f"⚠️ Ошибка патча: {e}")
