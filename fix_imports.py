import sys
import os

# Простой патч для совместимости
try:
    import urllib3
    sys.modules['telegram.vendor.ptb_urllib3.urllib3'] = urllib3
    print("✅ Патч применен")
except Exception as e:
    print(f"⚠️ Патч не применен: {e}")
