"""
URL маршруты для Auth API

Роуты:

1. GET  /auth/csrf   - Получить CSRF токен
2. POST /auth/login  - Авторизация пользователя
3. POST /auth/logout - Разлогинить пользователя
"""
from django.urls import path
from . import views

app_name = 'auth_api'

urlpatterns = [
    # CSRF Token (1)
    path('csrf', views.get_csrf_token, name='get_csrf_token'),
    
    # Login (2)
    path('login', views.login_user, name='login_user'),
    
    # Logout (3)
    path('logout', views.logout_user, name='logout_user'),
]

