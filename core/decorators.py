"""
Декораторы для авторизации и проверки прав доступа
"""
from functools import wraps
from django.http import JsonResponse


def login_required_api(view_func):
    """
    Декоратор для проверки авторизации пользователя через сессию.
    
    Если пользователь не авторизован - возвращает 401.
    Используется для API эндпоинтов.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse(
                {
                    "success": False,
                    "error": "Требуется авторизация",
                    "redirect": "/login"
                },
                status=401
            )
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    """
    Декоратор для проверки что пользователь - администратор.
    
    Сначала проверяет авторизацию, затем роль.
    Если не админ - возвращает 403.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Проверяем авторизацию
        if not request.user.is_authenticated:
            return JsonResponse(
                {
                    "success": False,
                    "error": "Требуется авторизация",
                    "redirect": "/login"
                },
                status=401
            )
        
        # Проверяем роль
        if request.user.role != 'admin':
            return JsonResponse(
                {
                    "success": False,
                    "error": "Недостаточно прав. Требуется роль администратора."
                },
                status=403
            )
        
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_or_self_required(view_func):
    """
    Декоратор для проверки что пользователь - администратор ИЛИ редактирует себя.
    
    Используется для /settings/employees/{id} где:
    - Админ может редактировать любого
    - Пользователь может редактировать только себя
    
    Требует параметр employee_id в URL.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Проверяем авторизацию
        if not request.user.is_authenticated:
            return JsonResponse(
                {
                    "success": False,
                    "error": "Требуется авторизация",
                    "redirect": "/login"
                },
                status=401
            )
        
        # Получаем ID сотрудника из URL
        employee_id = kwargs.get('employee_id')
        
        # Админ может всё
        if request.user.role == 'admin':
            return view_func(request, *args, **kwargs)
        
        # Пользователь может редактировать только себя
        if employee_id and int(employee_id) == request.user.id:
            return view_func(request, *args, **kwargs)
        
        return JsonResponse(
            {
                "success": False,
                "error": "Недостаточно прав. Вы можете редактировать только свой профиль."
            },
            status=403
        )
    return wrapper

