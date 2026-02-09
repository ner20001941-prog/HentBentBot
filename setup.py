from setuptools import setup, find_packages

setup(
    name="telegram-bot-fix",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'python-telegram-bot==13.15',
    ],
    # Добавляем заглушку для imghdr
    py_modules=['imghdr'],
)