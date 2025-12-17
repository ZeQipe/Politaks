"""
Кастомные middleware для Politaks
"""
from django.shortcuts import redirect
from django.contrib.auth import logout


class AdminSuperuserMiddleware:
    """
    Middleware для проверки доступа к админ-панели.
    
    Если пользователь пытается зайти в /admin/, но не является суперюзером:
    1. Разлогиниваем его
    2. Редиректим на страницу авторизации админ-панели
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Проверяем, является ли запрос к админ-панели
        if request.path.startswith('/admin/'):
            # Пропускаем страницу логина админки
            if request.path == '/admin/login/' or request.path == '/admin/logout/':
                return self.get_response(request)
            
            # Если пользователь авторизован, но не суперюзер
            if request.user.is_authenticated and not request.user.is_superuser:
                # Разлогиниваем
                logout(request)
                # Редиректим на страницу авторизации админ-панели
                return redirect('/admin/login/?next=' + request.path)
        
        return self.get_response(request)

