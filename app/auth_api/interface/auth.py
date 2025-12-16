"""
Функции авторизации для Auth API
"""
import secrets
import time
from django.conf import settings
from app.users.models import User


# Хранилище CSRF токенов (в production лучше использовать Redis/DB)
# Формат: {token: {"created_at": timestamp, "used": bool}}
_csrf_tokens = {}


def verify_bearer_token(auth_header: str) -> bool:
    """
    Проверка Bearer токена
    
    Сравнивает токен из заголовка с API_BEARER_TOKEN из .env
    
    Args:
        auth_header: Значение заголовка Authorization
    
    Returns:
        bool: True если токен валидный
    """
    if not auth_header:
        return False
    
    parts = auth_header.split(' ')
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        return False
    
    token = parts[1]
    expected_token = getattr(settings, 'API_BEARER_TOKEN', '')
    
    return token == expected_token


def _get_csrf_ttl() -> int:
    """Получить TTL для CSRF токенов из настроек"""
    return getattr(settings, 'CSRF_TOKEN_TTL', 300)


def generate_csrf_token() -> str:
    """
    Генерация CSRF токена
    
    Returns:
        str: Сгенерированный CSRF токен
    """
    # Очищаем старые токены
    _cleanup_expired_tokens()
    
    # Генерируем новый токен
    token = secrets.token_hex(32)
    _csrf_tokens[token] = {
        "created_at": time.time(),
        "used": False
    }
    
    return token


def verify_csrf_token(token: str) -> bool:
    """
    Проверка CSRF токена
    
    Args:
        token: CSRF токен для проверки
    
    Returns:
        bool: True если токен валидный и не использован
    """
    if not token or token not in _csrf_tokens:
        return False
    
    token_data = _csrf_tokens[token]
    ttl = _get_csrf_ttl()
    
    # Проверяем срок действия
    if time.time() - token_data["created_at"] > ttl:
        del _csrf_tokens[token]
        return False
    
    # Проверяем что токен не использован
    if token_data["used"]:
        return False
    
    # Помечаем токен как использованный
    _csrf_tokens[token]["used"] = True
    
    return True


def _cleanup_expired_tokens():
    """Очистка просроченных CSRF токенов"""
    current_time = time.time()
    ttl = _get_csrf_ttl()
    expired = [
        token for token, data in _csrf_tokens.items()
        if current_time - data["created_at"] > ttl
    ]
    for token in expired:
        del _csrf_tokens[token]


def authenticate_user(username: str, password: str):
    """
    Аутентификация пользователя по логину и паролю
    
    Args:
        username: Логин пользователя
        password: Пароль пользователя
    
    Returns:
        dict: {"success": bool, "user": User|None, "message": str}
    """
    try:
        if not username or not password:
            return {
                "success": False,
                "user": None,
                "message": "Логин и пароль обязательны"
            }
        
        # Ищем пользователя по логину
        try:
            user = User.objects.get(login=username)
        except User.DoesNotExist:
            return {
                "success": False,
                "user": None,
                "message": "Неверный логин или пароль"
            }
        
        # Проверяем что пользователь активен
        if not user.is_active:
            return {
                "success": False,
                "user": None,
                "message": "Пользователь деактивирован"
            }
        
        # Проверяем пароль
        if not user.check_password(password):
            return {
                "success": False,
                "user": None,
                "message": "Неверный логин или пароль"
            }
        
        return {
            "success": True,
            "user": user,
            "message": "Успешная авторизация"
        }
        
    except Exception as e:
        return {
            "success": False,
            "user": None,
            "message": f"Ошибка авторизации: {str(e)}"
        }

