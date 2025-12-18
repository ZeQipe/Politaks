"""
Views для Auth API
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout

from .interface.auth import (
    verify_bearer_token,
    generate_csrf_token,
    verify_csrf_token,
    authenticate_user
)


@csrf_exempt
@require_http_methods(["GET"])
def get_csrf_token(request):
    """
    GET /auth/csrf - Получить CSRF токен
    
    Headers:
        Authorization: Bearer <token>
    
    Response:
        200: {"csrfToken": "abc123xyz456"}
        401: {"error": "Invalid bearer token"}
    """
    # Проверяем Bearer токен
    auth_header = request.headers.get('Authorization', '')
    
    if not verify_bearer_token(auth_header):
        return JsonResponse(
            {"error": "Invalid bearer token"},
            status=401
        )
    
    # Генерируем CSRF токен
    csrf_token = generate_csrf_token()
    
    return JsonResponse(
        {"csrfToken": csrf_token},
        status=200
    )


@csrf_exempt
@require_http_methods(["POST"])
def login_user(request):
    """
    POST /auth/login - Авторизация пользователя
    
    Headers:
        X-CSRF-Token: <csrf_token>
    
    Query Parameters:
        username: Логин пользователя
        password: Пароль пользователя
    
    Response:
        200: {"success": true, "message": "Успешная авторизация"}
              + Set-Cookie: sessionid=...
        401: {"success": false, "message": "Неверный логин или пароль"}
        403: {"error": "Invalid CSRF token"}
    
    Note: Bearer токен НЕ проверяется здесь (только в /auth/csrf)
    """
    # Проверяем CSRF токен (обязателен для login)
    csrf_token = request.headers.get('X-CSRF-Token', '')
    
    if not verify_csrf_token(csrf_token):
        return JsonResponse(
            {"error": "Invalid CSRF token"},
            status=403
        )
    
    # Получаем параметры из query string
    username = request.GET.get('username', '')
    password = request.GET.get('password', '')
    
    # Аутентифицируем пользователя
    result = authenticate_user(username, password)
    
    if not result["success"]:
        return JsonResponse(
            {
                "success": False,
                "message": result["message"]
            },
            status=401
        )
    
    # Создаём сессию Django
    user = result["user"]
    login(request, user)
    
    # Формируем ответ с URL для редиректа
    response = JsonResponse(
        {
            "success": True,
            "message": result["message"],
            "redirectUrl": "/"
        },
        status=200
    )
    
    # Cookie устанавливается автоматически Django при login()
    # Но можно явно установить параметры если нужно:
    # response.set_cookie('sessionid', request.session.session_key, httponly=True, samesite='Lax')
    
    return response


@csrf_exempt
@require_http_methods(["GET"])
def logout_user(request):
    """
    GET /api/auth/logout - Разлогинить и редиректнуть на /login
    
    Использование: window.location.href = '/api/auth/logout'
    или <a href="/api/auth/logout">Выйти</a>
    """
    from django.shortcuts import redirect
    
    logout(request)
    
    response = redirect('/login')
    response.delete_cookie('sessionid')
    
    return response

