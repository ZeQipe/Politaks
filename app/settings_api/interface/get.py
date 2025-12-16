"""
Функции получения данных для Settings API
Возвращают данные в формате OpenAPI спецификации
"""
from app.users.models import User, UserAssistant
from app.config.models import Models, Assistant
from app.product.models import Satellite, Products


def get_user_profile(user_id: int):
    """
    Получить данные профиля пользователя
    
    GET /settings/user
    
    Returns:
        dict: {"status": "success", "data": {...}}
    """
    try:
        user = User.objects.get(id=user_id)
        
        return {
            "status": "success",
            "data": {
                "id": str(user.id),
                "firstName": user.firstName,
                "lastName": user.lastName,
                "excelBaseUrl": user.default_excel_url or ""
            }
        }
    except User.DoesNotExist:
        return {
            "status": "error",
            "error": f"Пользователь с ID '{user_id}' не найден"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Ошибка при получении профиля: {str(e)}"
        }


def get_task_sheet_mappings(user_id: int):
    """
    Получить маппинги задач на листы Excel для пользователя
    
    GET /settings/task-sheet-mappings
    
    Returns:
        dict: {"status": "success", "data": [...]}
    """
    try:
        # Получаем все ассистенты
        assistants = Assistant.objects.all().order_by('id')
        
        # Получаем маппинги пользователя
        user_mappings = {
            ua.assistant_id: ua.sheets_id
            for ua in UserAssistant.objects.filter(user_id=user_id)
        }
        
        data = []
        for assistant in assistants:
            # Если у пользователя есть маппинг - берём его sheets_id
            # Иначе берём default_sheets_id из ассистента
            sheets_id = user_mappings.get(assistant.id)
            if sheets_id is None:
                sheets_id = assistant.default_sheets_id or 0
            
            data.append({
                "taskId": str(assistant.id),
                "taskName": assistant.title,
                "sheetId": sheets_id
            })
        
        return {
            "status": "success",
            "data": data
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Ошибка при получении маппингов: {str(e)}"
        }


def get_available_domains():
    """
    Получить доступные домены для товаров
    
    GET /settings/domains
    
    Returns:
        dict: {"status": "success", "data": [...]}
    """
    try:
        satellites = Satellite.objects.all().order_by('id')
        
        data = []
        for satellite in satellites:
            data.append({
                "id": str(satellite.id),
                "name": satellite.title,
                "domain": satellite.domen
            })
        
        return {
            "status": "success",
            "data": data
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Ошибка при получении доменов: {str(e)}"
        }


def get_goods_list(user_id: int):
    """
    Получить список товаров пользователя
    
    GET /settings/goods/list
    
    Returns:
        dict: {"success": "true", "data": [...]}
    """
    try:
        products = Products.objects.filter(created_by_id=user_id).order_by('id')
        
        data = []
        for product in products:
            # Получаем выбранные домены
            selected_domains = []
            for satellite in product.satelitDomens.all():
                selected_domains.append({
                    "id": str(satellite.id),
                    "name": satellite.title,
                    "domain": satellite.domen
                })
            
            data.append({
                "id": str(product.id),
                "name": product.title,
                "description": product.description or "",
                "baseUrl": product.baseLink or "",
                "satelliteUrl": product.satelitLink or "",
                "selectedDomain": selected_domains
            })
        
        return {
            "success": "true",
            "data": data
        }
    except Exception as e:
        return {
            "success": "false",
            "error": f"Ошибка при получении товаров: {str(e)}"
        }


def get_models_list():
    """
    Получить список AI моделей
    
    GET /settings/models
    
    Returns:
        dict: {"success": "true", "data": [...]}
    """
    try:
        models = Models.objects.all().order_by('id')
        
        data = []
        for model in models:
            data.append({
                "id": str(model.id),
                "name": model.name,
                "key": model.get_key(),  # Расшифровываем ключ
                "url": model.url
            })
        
        return {
            "success": "true",
            "data": data
        }
    except Exception as e:
        return {
            "success": "false",
            "error": f"Ошибка при получении моделей: {str(e)}"
        }


def get_satellites_list():
    """
    Получить список доменов-сателлитов
    
    GET /settings/satellites
    
    Returns:
        dict: {"success": "true", "data": [...]}
    """
    try:
        satellites = Satellite.objects.all().order_by('id')
        
        data = []
        for satellite in satellites:
            data.append({
                "id": str(satellite.id),
                "name": satellite.title,
                "domain": satellite.domen
            })
        
        return {
            "success": "true",
            "data": data
        }
    except Exception as e:
        return {
            "success": "false",
            "error": f"Ошибка при получении сателлитов: {str(e)}"
        }


def get_employees_list():
    """
    Получить список сотрудников
    
    GET /settings/employees
    
    Returns:
        dict: {"success": "true", "data": [...]}
    """
    try:
        users = User.objects.filter(is_active=True).order_by('id')
        
        data = []
        for user in users:
            data.append({
                "id": str(user.id),
                "firstName": user.firstName,
                "lastName": user.lastName,
                "role": user.role
            })
        
        return {
            "success": "true",
            "data": data
        }
    except Exception as e:
        return {
            "success": "false",
            "error": f"Ошибка при получении сотрудников: {str(e)}"
        }


def get_roles_list():
    """
    Получить список ролей (из констант)
    
    GET /settings/roles
    
    Returns:
        dict: {"success": "true", "data": [...]}
    """
    try:
        # Роли из констант User.ROLE_CHOICES
        roles_data = []
        for idx, (key, name) in enumerate(User.ROLE_CHOICES, start=1):
            roles_data.append({
                "id": str(idx),
                "name": name,
                "key": key
            })
        
        return {
            "success": "true",
            "data": roles_data
        }
    except Exception as e:
        return {
            "success": "false",
            "error": f"Ошибка при получении ролей: {str(e)}"
        }

