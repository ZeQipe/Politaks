"""
URL маршруты для Settings API

Все 22 роута согласно OpenAPI спецификации:

User Profile:
1. GET  /settings/user                    - Получить данные пользователя
2. PATCH /settings/user                   - Обновить профиль пользователя

Task Sheet Mappings:
3. GET  /settings/task-sheet-mappings     - Получить маппинги задач
4. PATCH /settings/task-sheet-mappings    - Обновить маппинги задач

Domains:
5. GET  /settings/domains                 - Получить доступные домены

Goods:
6. GET  /settings/goods/list              - Получить список товаров
7. POST /settings/goods                   - Создать товар
8. PATCH /settings/goods/{id}             - Обновить товар
9. DELETE /settings/goods/{id}            - Удалить товар

AI Models:
10. GET  /settings/models                 - Получить список AI моделей
11. POST /settings/models                 - Создать AI модель
12. PATCH /settings/models/{id}           - Обновить AI модель
13. DELETE /settings/models/{id}          - Удалить AI модель

Satellites:
14. GET  /settings/satellites             - Получить список доменов-сателлитов
15. POST /settings/satellites             - Создать домен-сателлит
16. PATCH /settings/satellites/{id}       - Обновить домен-сателлит
17. DELETE /settings/satellites/{id}      - Удалить домен-сателлит

Employees:
18. GET  /settings/employees              - Получить список сотрудников
19. POST /settings/employees              - Создать сотрудника
20. PATCH /settings/employees/{id}        - Обновить сотрудника
21. DELETE /settings/employees/{id}       - Удалить сотрудника

Roles:
22. GET  /settings/roles                  - Получить список ролей
"""
from django.urls import path
from . import views

app_name = 'settings_api'

urlpatterns = [
    # User Profile (1-2)
    path('user', views.user_profile, name='user_profile'),
    
    # Task Sheet Mappings (3-4)
    path('task-sheet-mappings', views.task_sheet_mappings, name='task_sheet_mappings'),
    
    # Domains (5)
    path('domains', views.available_domains, name='available_domains'),
    
    # Goods (6-9)
    path('goods/list', views.goods_list, name='goods_list'),
    path('goods', views.goods_create, name='goods_create'),
    path('goods/<int:goods_id>', views.goods_detail, name='goods_detail'),
    
    # AI Models (10-13)
    path('models', views.models_list, name='models_list'),
    path('models/<int:model_id>', views.models_detail, name='models_detail'),
    
    # Satellites (14-17)
    path('satellites', views.satellites_list, name='satellites_list'),
    path('satellites/<int:satellite_id>', views.satellites_detail, name='satellites_detail'),
    
    # Employees (18-21)
    path('employees', views.employees_list, name='employees_list'),
    path('employees/<int:employee_id>', views.employees_detail, name='employees_detail'),
    
    # Roles (22)
    path('roles', views.roles_list, name='roles_list'),
]

