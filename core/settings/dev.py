"""
Настройки для окружения разработки (Development)
"""
import os
from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-@h2o*k-^&g#q(r*i-ddv$b2$9vw$jfzrvqm2nl^lrq5j85pb(3'
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': BASE_DIR / os.environ.get('DB_NAME', 'db.sqlite3'),
    }
}


# Development-specific settings
# Показывать подробные ошибки
DEBUG_PROPAGATE_EXCEPTIONS = True

# Логирование для разработки
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Django Debug Toolbar (если установлен)
try:
    import debug_toolbar
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE
    INTERNAL_IPS = ['127.0.0.1', 'localhost']
except ImportError:
    pass

print("⚙️  Режим разработки (Development) активирован")
print(f"📊 DEBUG: {DEBUG}")
print(f"🔑 SECRET_KEY: {'установлен' if SECRET_KEY else 'не установлен'}")
print(f"🌐 ALLOWED_HOSTS: {ALLOWED_HOSTS}")

