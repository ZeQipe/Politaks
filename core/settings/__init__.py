"""
Инициализация настроек Django с поддержкой окружений
"""
import os

# Определяем окружение из переменной DJANGO_ENV
# По умолчанию - development
environment = os.environ.get('DJANGO_ENV', 'development')

if environment == 'production':
    from .prod import *
else:
    from .dev import *

print(f"🚀 Django запущен в режиме: {environment}")

