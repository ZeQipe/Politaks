"""
Утилиты для шифрования/дешифрования API ключей
"""

import os
from cryptography.fernet import Fernet
from django.conf import settings


def get_encryption_key():
    """Получает ключ шифрования из переменных окружения"""
    key = os.environ.get('ENCRYPTION_KEY')
    if not key:
        raise ValueError("ENCRYPTION_KEY не установлен в переменных окружения")
    return key.encode()


def encrypt_api_key(api_key: str) -> str:
    """
    Шифрует API ключ
    
    Args:
        api_key: Оригинальный API ключ
    
    Returns:
        Зашифрованная строка (base64)
    """
    if not api_key:
        return ""
    
    fernet = Fernet(get_encryption_key())
    encrypted = fernet.encrypt(api_key.encode())
    return encrypted.decode()


def decrypt_api_key(encrypted_key: str) -> str:
    """
    Расшифровывает API ключ
    
    Args:
        encrypted_key: Зашифрованная строка
    
    Returns:
        Оригинальный API ключ или маскированная строка при ошибке
    """
    if not encrypted_key:
        return ""
    
    try:
        fernet = Fernet(get_encryption_key())
        decrypted = fernet.decrypt(encrypted_key.encode())
        return decrypted.decode()
    except Exception:
        # Если не удалось расшифровать - возвращаем маскированную строку
        # (данные не зашифрованы или ключ изменился)
        if len(encrypted_key) > 8:
            return encrypted_key[:4] + "****" + encrypted_key[-4:]
        return "****"


def generate_encryption_key() -> str:
    """
    Генерирует новый ключ шифрования
    
    Returns:
        Ключ шифрования (base64 строка)
    """
    return Fernet.generate_key().decode()

