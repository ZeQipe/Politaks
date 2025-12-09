"""
Инициализация настроек Django с поддержкой окружений
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Загружаем .env файл
env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(env_path)

# Определяем окружение из переменной DJANGO_ENV
# По умолчанию - development
environment = os.environ.get('DJANGO_ENV', 'development')

if environment == 'production':
    from .prod import *
else:
    from .dev import *

