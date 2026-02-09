# setup.py
from setuptools import setup, find_packages

setup(
    name="telegram-bot",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'python-telegram-bot==13.15',
        'urllib3==1.26.18',
        'six==1.16.0',
    ],
)