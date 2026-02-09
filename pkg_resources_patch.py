# pkg_resources_patch.py
"""
Патч для имитации pkg_resources в Python 3.14+
"""
import sys
import types


class Distribution:
    def __init__(self, version='1.0.0'):
        self.version = version

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, value):
        self._version = value


def get_distribution(name):
    """Имитация pkg_resources.get_distribution"""
    versions = {
        'setuptools': '82.0.0',
        'python-telegram-bot': '13.15',
        'APScheduler': '3.6.3',
        'tornado': '6.1',
        'urllib3': '1.26.18',
        'six': '1.16.0',
    }
    return Distribution(versions.get(name, '1.0.0'))


class DistributionNotFound(Exception):
    pass


# Создаем фиктивный модуль
pkg_resources_module = types.ModuleType('pkg_resources')
pkg_resources_module.get_distribution = get_distribution
pkg_resources_module.DistributionNotFound = DistributionNotFound
pkg_resources_module.__version__ = '1.0.0'

# Заменяем в sys.modules
sys.modules['pkg_resources'] = pkg_resources_module