"""
Views для Settings API
"""
import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from core.decorators import login_required_api, admin_required, admin_or_self_required

from .interface.get import (
    get_user_profile,
    get_task_sheet_mappings,
    get_available_domains,
    get_goods_list,
    get_models_list,
    get_satellites_list,
    get_employees_list,
    get_roles_list
)
from .interface.set import (
    create_goods,
    create_model,
    create_satellite,
    create_employee
)
from .interface.put import (
    update_user_profile,
    update_task_sheet_mappings,
    update_goods,
    update_model,
    update_satellite,
    update_employee
)
from .interface.delete import (
    delete_goods,
    delete_model,
    delete_satellite,
    delete_employee
)


# ========================================
# USER PROFILE
# ========================================

@csrf_exempt
@require_http_methods(["GET", "PATCH"])
@login_required_api
def user_profile(request):
    """
    GET /settings/user - Получить данные пользователя
    PATCH /settings/user - Обновить профиль пользователя
    
    Авторизация: требуется (по сессии)
    """
    user_id = request.user.id
    
    if request.method == "GET":
        result = get_user_profile(user_id)
        
        if result.get("status") == "success":
            return JsonResponse(result, status=200)
        else:
            return JsonResponse(result, status=404)
    
    elif request.method == "PATCH":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Некорректный JSON"}, status=400)
        
        result = update_user_profile(
            user_id=user_id,
            first_name=data.get("firstName"),
            last_name=data.get("lastName"),
            current_password=data.get("currentPassword"),
            new_password=data.get("newPassword"),
            excel_base_url=data.get("excelBaseUrl")
        )
        
        if result.get("success"):
            return JsonResponse(result, status=200)
        else:
            return JsonResponse(result, status=400)


# ========================================
# TASK SHEET MAPPINGS
# ========================================

@csrf_exempt
@require_http_methods(["GET", "PATCH"])
@login_required_api
def task_sheet_mappings(request):
    """
    GET /settings/task-sheet-mappings - Получить маппинги задач
    PATCH /settings/task-sheet-mappings - Обновить маппинги задач
    
    Авторизация: требуется (по сессии)
    """
    user_id = request.user.id
    
    if request.method == "GET":
        result = get_task_sheet_mappings(user_id)
        
        if result.get("status") == "success":
            return JsonResponse(result, status=200)
        else:
            return JsonResponse(result, status=500)
    
    elif request.method == "PATCH":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Некорректный JSON"}, status=400)
        
        mappings = data.get("mappings", [])
        
        result = update_task_sheet_mappings(user_id, mappings)
        
        if result.get("success"):
            return JsonResponse(result, status=200)
        else:
            return JsonResponse(result, status=400)


# ========================================
# DOMAINS (for goods)
# ========================================

@require_http_methods(["GET"])
@login_required_api
def available_domains(request):
    """
    GET /settings/domains - Получить доступные домены
    
    Авторизация: требуется (по сессии)
    """
    result = get_available_domains()
    
    if result.get("status") == "success":
        return JsonResponse(result, status=200)
    else:
        return JsonResponse(result, status=500)


# ========================================
# GOODS
# ========================================

@require_http_methods(["GET"])
@login_required_api
def goods_list(request):
    """
    GET /settings/goods/list - Получить список товаров
    
    Авторизация: требуется (по сессии)
    """
    user_id = request.user.id
    result = get_goods_list(user_id)
    
    if result.get("success") == "true":
        return JsonResponse(result, status=200)
    else:
        return JsonResponse(result, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required_api
def goods_create(request):
    """
    POST /settings/goods - Создать товар
    
    Авторизация: требуется (по сессии)
    Создатель записывается в created_by
    """
    user_id = request.user.id
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": "false", "error": "Некорректный JSON"}, status=400)
    
    result = create_goods(
        user_id=user_id,
        name=data.get("name", ""),
        description=data.get("description", ""),
        base_url=data.get("baseUrl", ""),
        satellite_url=data.get("satelliteUrl", ""),
        selected_domains=data.get("selectedDomain", [])
    )
    
    if result.get("success") == "true":
        return JsonResponse(result, status=200)
    else:
        return JsonResponse(result, status=400)


@csrf_exempt
@require_http_methods(["PATCH", "DELETE"])
@login_required_api
def goods_detail(request, goods_id):
    """
    PATCH /settings/goods/{id} - Обновить товар (любой авторизованный)
    DELETE /settings/goods/{id} - Удалить товар (только админ)
    
    Авторизация: требуется (по сессии)
    При PATCH: last_edit_user устанавливается в текущего пользователя
    При DELETE: только для админов
    """
    user_id = request.user.id
    
    if request.method == "PATCH":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"success": "false", "error": "Некорректный JSON"}, status=400)
        
        result = update_goods(
            goods_id=goods_id,
            user_id=user_id,
            name=data.get("name", ""),
            description=data.get("description", ""),
            base_url=data.get("baseUrl", ""),
            satellite_url=data.get("satelliteUrl", ""),
            selected_domains=data.get("selectedDomain", [])
        )
        
        if result.get("success") == "true":
            return JsonResponse(result, status=200)
        else:
            return JsonResponse(result, status=400)
    
    elif request.method == "DELETE":
        # Только админ может удалять товары
        if request.user.role != 'admin':
            return JsonResponse(
                {"success": "false", "error": "Недостаточно прав. Удалять товары может только администратор."},
                status=403
            )
        
        result = delete_goods(goods_id, user_id)
        
        if result.get("success") == "true":
            return JsonResponse(result, status=200)
        else:
            return JsonResponse(result, status=400)


# ========================================
# AI MODELS
# ========================================

@csrf_exempt
@require_http_methods(["GET", "POST"])
@login_required_api
def models_list(request):
    """
    GET /settings/models - Получить список AI моделей (любой авторизованный)
    POST /settings/models - Создать AI модель (только админ)
    
    Авторизация: требуется (по сессии)
    """
    if request.method == "GET":
        result = get_models_list()
        
        if result.get("success") == "true":
            return JsonResponse(result, status=200)
        else:
            return JsonResponse(result, status=500)
    
    elif request.method == "POST":
        # Только админ может создавать модели
        if request.user.role != 'admin':
            return JsonResponse(
                {"success": "false", "error": "Недостаточно прав. Создавать модели может только администратор."},
                status=403
            )
        
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"success": "false", "error": "Некорректный JSON"}, status=400)
        
        result = create_model(
            name=data.get("name", ""),
            key=data.get("key", ""),
            url=data.get("url", "")
        )
        
        if result.get("success") == "true":
            return JsonResponse(result, status=200)
        else:
            return JsonResponse(result, status=400)


@csrf_exempt
@require_http_methods(["PATCH", "DELETE"])
@admin_required
def models_detail(request, model_id):
    """
    PATCH /settings/models/{id} - Обновить AI модель
    DELETE /settings/models/{id} - Удалить AI модель
    
    Авторизация: только админ
    """
    if request.method == "PATCH":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"success": "false", "error": "Некорректный JSON"}, status=400)
        
        result = update_model(
            model_id=model_id,
            name=data.get("name", ""),
            key=data.get("key", ""),
            url=data.get("url", "")
        )
        
        if result.get("success") == "true":
            return JsonResponse(result, status=200)
        else:
            return JsonResponse(result, status=400)
    
    elif request.method == "DELETE":
        result = delete_model(model_id)
        
        if result.get("success") == "true":
            return JsonResponse(result, status=200)
        else:
            return JsonResponse(result, status=400)


# ========================================
# SATELLITES
# ========================================

@csrf_exempt
@require_http_methods(["GET", "POST"])
@login_required_api
def satellites_list(request):
    """
    GET /settings/satellites - Получить список доменов-сателлитов (любой авторизованный)
    POST /settings/satellites - Создать домен-сателлит (только админ)
    
    Авторизация: требуется (по сессии)
    """
    if request.method == "GET":
        result = get_satellites_list()
        
        if result.get("success") == "true":
            return JsonResponse(result, status=200)
        else:
            return JsonResponse(result, status=500)
    
    elif request.method == "POST":
        # Только админ может создавать сателлиты
        if request.user.role != 'admin':
            return JsonResponse(
                {"success": "false", "error": "Недостаточно прав. Создавать сателлиты может только администратор."},
                status=403
            )
        
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"success": "false", "error": "Некорректный JSON"}, status=400)
        
        result = create_satellite(
            name=data.get("name", ""),
            domain=data.get("domain", "")
        )
        
        if result.get("success") == "true":
            return JsonResponse(result, status=200)
        else:
            return JsonResponse(result, status=400)


@csrf_exempt
@require_http_methods(["PATCH", "DELETE"])
@admin_required
def satellites_detail(request, satellite_id):
    """
    PATCH /settings/satellites/{id} - Обновить домен-сателлит
    DELETE /settings/satellites/{id} - Удалить домен-сателлит
    
    Авторизация: только админ
    """
    if request.method == "PATCH":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"success": "false", "error": "Некорректный JSON"}, status=400)
        
        result = update_satellite(
            satellite_id=satellite_id,
            name=data.get("name", ""),
            domain=data.get("domain", "")
        )
        
        if result.get("success") == "true":
            return JsonResponse(result, status=200)
        else:
            return JsonResponse(result, status=400)
    
    elif request.method == "DELETE":
        result = delete_satellite(satellite_id)
        
        if result.get("success") == "true":
            return JsonResponse(result, status=200)
        else:
            return JsonResponse(result, status=400)


# ========================================
# EMPLOYEES
# ========================================

@csrf_exempt
@require_http_methods(["GET", "POST"])
@login_required_api
def employees_list(request):
    """
    GET /settings/employees - Получить список сотрудников (любой авторизованный)
    POST /settings/employees - Создать сотрудника (только админ)
    
    Авторизация: требуется (по сессии)
    """
    if request.method == "GET":
        result = get_employees_list()
        
        if result.get("success") == "true":
            return JsonResponse(result, status=200)
        else:
            return JsonResponse(result, status=500)
    
    elif request.method == "POST":
        # Только админ может создавать сотрудников
        if request.user.role != 'admin':
            return JsonResponse(
                {"success": "false", "error": "Недостаточно прав. Создавать сотрудников может только администратор."},
                status=403
            )
        
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"success": "false", "error": "Некорректный JSON"}, status=400)
        
        result = create_employee(
            first_name=data.get("firstName", ""),
            last_name=data.get("lastName", ""),
            role=data.get("role", ""),
            password=data.get("newPassword", "")
        )
        
        if result.get("success") == "true":
            return JsonResponse(result, status=200)
        else:
            return JsonResponse(result, status=400)


@csrf_exempt
@require_http_methods(["PATCH", "DELETE"])
@login_required_api
def employees_detail(request, employee_id):
    """
    PATCH /settings/employees/{id} - Обновить сотрудника
        - Админ может редактировать любого
        - Пользователь может редактировать только себя
    DELETE /settings/employees/{id} - Удалить сотрудника (только админ)
    
    Авторизация: требуется (по сессии)
    """
    if request.method == "PATCH":
        # Проверка прав: админ может всех, остальные - только себя
        if request.user.role != 'admin' and int(employee_id) != request.user.id:
            return JsonResponse(
                {"success": "false", "error": "Недостаточно прав. Вы можете редактировать только свой профиль."},
                status=403
            )
        
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"success": "false", "error": "Некорректный JSON"}, status=400)
        
        result = update_employee(
            employee_id=employee_id,
            first_name=data.get("firstName", ""),
            last_name=data.get("lastName", ""),
            role=data.get("role", ""),
            new_password=data.get("newPassword"),
            confirm_password=data.get("confirmPassword")
        )
        
        if result.get("success") == "true":
            return JsonResponse(result, status=200)
        else:
            return JsonResponse(result, status=400)
    
    elif request.method == "DELETE":
        # Только админ может удалять сотрудников
        if request.user.role != 'admin':
            return JsonResponse(
                {"success": "false", "error": "Недостаточно прав. Удалять сотрудников может только администратор."},
                status=403
            )
        
        result = delete_employee(employee_id)
        
        if result.get("success") == "true":
            return JsonResponse(result, status=200)
        else:
            return JsonResponse(result, status=400)


# ========================================
# ROLES
# ========================================

@require_http_methods(["GET"])
@login_required_api
def roles_list(request):
    """
    GET /settings/roles - Получить список ролей
    
    Авторизация: требуется (по сессии)
    """
    result = get_roles_list()
    
    if result.get("success") == "true":
        return JsonResponse(result, status=200)
    else:
        return JsonResponse(result, status=500)


# ========================================
# EXCEL LINK
# ========================================

@require_http_methods(["GET"])
@login_required_api
def excel_link(request):
    """
    GET /settings/link - Получить базовую Excel ссылку из профиля
    
    Авторизация: требуется (по сессии)
    """
    link = request.user.default_excel_url or ""
    
    return JsonResponse({
        "success": "true",
        "link": link
    }, status=200)