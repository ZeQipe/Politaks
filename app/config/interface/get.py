"""
Функции получения данных конфигурации
Возвращают данные в едином формате
"""
import json
from django.utils import timezone
from ..models import Models, Assistant, AssistantInputer
from app.product.models import Satellite, Products
from app.response.models import Response


def get_filters_for_generation():
    """
    Получение фильтров для страницы генерации
    Только активные записи, labelPlacement = 'left'
    """
    return _build_filters_response(
        label_placement='left',
        only_active=True,
        only_with_history=False
    )


def get_filters_for_history():
    """
    Получение фильтров для страницы истории
    Возвращает 5 фильтров: tasks, models, domains, creators, sources
    labelPlacement = 'top'
    """
    return _build_history_filters_response()


def _build_filters_response(label_placement: str, only_active: bool, only_with_history: bool):
    """
    Формирование ответа с фильтрами
    
    Args:
        label_placement: 'left' или 'top'
        only_active: только активные записи
        only_with_history: только записи с историей в Response
    """
    try:
        # Получаем tasks (Assistant)
        tasks_items = _get_tasks_items(only_active, only_with_history)
        
        # Получаем models (Models)
        models_items = _get_models_items(only_active, only_with_history)
        
        # Получаем domains (Satellite + Основной)
        domains_items = _get_domains_items(only_active, only_with_history)
        
        return {
            "success": True,
            "data": {
                "tasks": {
                    "items": tasks_items,
                    "label": "Ассистенты",
                    "labelPlacement": label_placement
                },
                "models": {
                    "items": models_items,
                    "label": "Модель LLM",
                    "labelPlacement": label_placement
                },
                "domains": {
                    "items": domains_items,
                    "label": "Домен",
                    "labelPlacement": label_placement
                }
            },
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": f"Ошибка при получении фильтров: {str(e)}"
        }


def _get_tasks_items(only_active: bool, only_with_history: bool):
    """Получение списка задач (Assistant)"""
    queryset = Assistant.objects.all().order_by('id')
    
    if only_with_history:
        used_assistants = Response.objects.order_by().values_list('assistant', flat=True).distinct()
        queryset = queryset.filter(title__in=used_assistants)
    
    items = []
    for i, assistant in enumerate(queryset):
        items.append({
            "id": str(assistant.id),
            "label": assistant.title,
            "value": assistant.key_title,
            "default": i == 0  # Первый (наименьший ID) по умолчанию
        })
    
    return items


def _get_models_items(only_active: bool, only_with_history: bool):
    """Получение списка моделей (Models)"""
    queryset = Models.objects.all().order_by('id')
    
    if only_active:
        queryset = queryset.filter(is_active=True)
    
    if only_with_history:
        used_models = Response.objects.order_by().values_list('model', flat=True).distinct()
        queryset = queryset.filter(name__in=used_models)
    
    items = []
    for i, model in enumerate(queryset):
        items.append({
            "id": str(model.id),
            "label": model.name,
            "value": str(model.id),
            "default": i == 0  # Первый (наименьший ID) по умолчанию
        })
    
    return items


def _get_domains_items(only_active: bool, only_with_history: bool):
    """Получение списка доменов (Satellite + Основной)"""
    items = []
    
    # Добавляем "Основной" первым (всегда по умолчанию)
    items.append({
        "id": "main",
        "label": "Основной",
        "value": "main",
        "default": True
    })
    
    queryset = Satellite.objects.all().order_by('id')
    
    if only_with_history:
        used_domains = Response.objects.order_by().values_list('domen', flat=True).distinct()
        queryset = queryset.filter(domen__in=used_domains)
    
    for satellite in queryset:
        items.append({
            "id": str(satellite.id),
            "label": satellite.title,
            "value": str(satellite.id),
            "default": False
        })
    
    return items


def _get_creators_items():
    """Получение списка создателей из истории"""
    from app.users.models import User
    
    used_creators = Response.objects.order_by().values_list('user', flat=True).distinct()
    users = User.objects.filter(login__in=used_creators).order_by('id')
    
    items = []
    for i, user in enumerate(users):
        items.append({
            "id": user.login,
            "label": f"{user.firstName} {user.lastName}".strip() or user.login,
            "value": user.login,
            "default": i == 0
        })
    
    return items


def _get_sources_items():
    """Получение списка источников из истории"""
    used_sources = (
        Response.objects
        .order_by()
        .values_list('source', flat=True)
        .distinct()
    )
    
    source_labels = {
        'manual': 'Ручной ввод',
        'excel': 'Из Excel'
    }
    
    items = []
    for i, source in enumerate(used_sources):
        if source:
            items.append({
                "id": source,
                "label": source_labels.get(source, source),
                "value": source,
                "default": i == 0
            })
    
    return items


def _build_history_filters_response():
    """
    Формирование ответа с фильтрами для страницы истории
    Возвращает 5 фильтров: tasks, models, domains, creators, sources
    """
    try:
        label_placement = 'top'
        
        tasks_items = _get_tasks_items(only_active=False, only_with_history=True)
        models_items = _get_models_items(only_active=False, only_with_history=True)
        domains_items = _get_domains_items(only_active=False, only_with_history=True)
        creators_items = _get_creators_items()
        sources_items = _get_sources_items()
        
        return {
            "success": True,
            "data": {
                "tasks": {
                    "items": tasks_items,
                    "label": "Ассистенты",
                    "labelPlacement": label_placement
                },
                "models": {
                    "items": models_items,
                    "label": "Модель LLM",
                    "labelPlacement": label_placement
                },
                "domains": {
                    "items": domains_items,
                    "label": "Домен",
                    "labelPlacement": label_placement
                },
                "creators": {
                    "items": creators_items,
                    "label": "Создатель",
                    "labelPlacement": label_placement
                },
                "sources": {
                    "items": sources_items,
                    "label": "Источник",
                    "labelPlacement": label_placement
                }
            },
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": f"Ошибка при получении фильтров: {str(e)}"
        }


def get_form_config(task_id: str, domain_id: str):
    """
    Получение конфигурации формы для генерации
    
    Args:
        task_id: ID ассистента (строка)
        domain_id: ID домена ('main' или ID Satellite)
    
    Returns:
        dict: {"success": bool, "data": list, "error": str}
    """
    try:
        # Находим ассистента по ID
        try:
            assistant = Assistant.objects.get(id=task_id)
        except Assistant.DoesNotExist:
            return {
                "success": False,
                "data": None,
                "error": f"Ассистент с ID '{task_id}' не найден"
            }
        
        # Получаем связанные Inputer через AssistantInputer
        assistant_inputers = AssistantInputer.objects.filter(
            assistant=assistant
        ).select_related('inputer').order_by('order', 'id')
        
        # Формируем массив полей формы
        form_fields = []
        
        for ai in assistant_inputers:
            inputer = ai.inputer
            is_required = ai.required == 'required'
            
            # Формируем поле в зависимости от типа
            field = _build_form_field(inputer, is_required, domain_id)
            if field:
                form_fields.append(field)
        
        return {
            "success": True,
            "data": form_fields,
            "error": None
        }
        
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": f"Ошибка при получении конфигурации формы: {str(e)}"
        }


def _build_form_field(inputer, is_required: bool, domain_id: str):
    """
    Формирование JSON объекта поля формы в зависимости от типа
    
    Args:
        inputer: объект Inputer
        is_required: обязательность поля
        domain_id: ID домена для select
    """
    base_field = {
        "type": inputer.type,
        "name": inputer.name,
        "label": inputer.label,
        "required": is_required,
    }
    
    # single - однострочное поле
    if inputer.type == 'single':
        base_field["labelPlacement"] = "top"
        if inputer.placement:
            base_field["placeholder"] = inputer.placement
        return base_field
    
    # multiline - многострочное поле
    elif inputer.type == 'multiline':
        base_field["labelPlacement"] = "top"
        if inputer.placement:
            base_field["placeholder"] = inputer.placement
        base_field["size"] = inputer.get_size_code()  # s, m, l
        return base_field
    
    # photo - загрузка фото
    elif inputer.type == 'photo':
        base_field["labelPlacement"] = "left"
        return base_field
    
    # select - выбор из списка
    elif inputer.type == 'select':
        base_field["labelPlacement"] = "top"
        base_field["withSearch"] = inputer.select_search  # из модели
        base_field["multiple"] = inputer.multi_select  # из модели
        base_field["items"] = _get_select_items(inputer.type_select, domain_id)
        return base_field
    
    return None


def _get_select_items(type_select: str, domain_id: str):
    """
    Получение items для select в зависимости от type_select и домена
    
    Args:
        type_select: тип выбора ('product')
        domain_id: ID домена ('main' или ID Satellite)
    """
    items = []
    
    if type_select == 'product':
        # Получаем продукты в зависимости от домена
        if domain_id == 'main':
            # Основной домен - все продукты с baseLink
            products = Products.objects.filter(
                baseLink__isnull=False
            ).exclude(baseLink='').order_by('id')
        else:
            # Satellite - продукты связанные с этим сателлитом
            try:
                satellite = Satellite.objects.get(id=domain_id)
                products = satellite.products.all().order_by('id')
            except Satellite.DoesNotExist:
                products = Products.objects.none()
        
        for product in products:
            items.append({
                "id": str(product.id),
                "label": product.title
            })
    
    return items


def get_history(
    count: int = 10, 
    offset: int = 0, 
    task_id: str = None, 
    model_id: str = None, 
    domain_id: str = None,
    creator_id: str = None,
    source_id: str = None
):
    """
    Получение истории генераций
    
    Args:
        count: количество записей
        offset: смещение для пагинации
        task_id: ID ассистента (опционально, '_all' = все)
        model_id: ID модели (опционально, '_all' = все)
        domain_id: ID домена (опционально, 'main', ID Satellite или '_all')
        creator_id: логин создателя (опционально, '_all' = все)
        source_id: источник 'manual'/'excel' (опционально, '_all' = все)
    
    Returns:
        dict: {"success": bool, "data": list, "count": int, "error": str}
    """
    try:
        from ..models import Inputer
        
        queryset = Response.objects.all().order_by('-createAt')
        
        # Фильтрация по task (Assistant)
        # "_all" означает "все записи" - не применяем фильтр
        if task_id and task_id != '_all':
            try:
                assistant = Assistant.objects.get(id=task_id)
                queryset = queryset.filter(assistant=assistant.title)
            except Assistant.DoesNotExist:
                pass
        
        # Фильтрация по model
        # "_all" означает "все записи" - не применяем фильтр
        if model_id and model_id != '_all':
            try:
                model = Models.objects.get(id=model_id)
                queryset = queryset.filter(model=model.name)
            except Models.DoesNotExist:
                pass
        
        # Фильтрация по domain
        # "_all" означает "все записи" - не применяем фильтр
        if domain_id and domain_id != '_all':
            if domain_id == 'main':
                queryset = queryset.filter(domen='main')
            else:
                try:
                    satellite = Satellite.objects.get(id=domain_id)
                    queryset = queryset.filter(domen=satellite.domen)
                except Satellite.DoesNotExist:
                    pass
        
        # Фильтрация по creator (user login)
        # "_all" означает "все записи" - не применяем фильтр
        if creator_id and creator_id != '_all':
            queryset = queryset.filter(user=creator_id)
        
        # Фильтрация по source
        # "_all" означает "все записи" - не применяем фильтр
        if source_id and source_id != '_all':
            queryset = queryset.filter(source=source_id)
        
        # Общее количество записей (до пагинации)
        total_count = queryset.count()
        
        # TODO: временная заглушка — игнорируем count, возвращаем всё
        # queryset = queryset[offset:offset + count]
        
        # Кэш для Inputer labels
        inputer_labels = {inp.name: inp.label for inp in Inputer.objects.all()}
        
        # Формируем ответ
        data = []
        for response in queryset:
            # Парсим details из parametrs
            details = []
            try:
                params = json.loads(response.parametrs)
                if isinstance(params, list):
                    for param in params:
                        name = param.get('name', '')
                        value = param.get('value', '')
                        # Получаем label из Inputer или используем name
                        label = inputer_labels.get(name, name)
                        # Преобразуем value в строку если это список
                        if isinstance(value, list):
                            value = ', '.join(str(v) for v in value)
                        details.append({
                            "label": label,
                            "content": str(value)
                        })
            except (json.JSONDecodeError, TypeError):
                pass
            
            # Определяем отображаемый домен
            domain_display = response.domen
            if response.domen == 'main':
                domain_display = 'Основной'
            else:
                # Пытаемся найти title сателлита
                try:
                    sat = Satellite.objects.get(domen=response.domen)
                    domain_display = sat.title
                except Satellite.DoesNotExist:
                    pass
            
            data.append({
                "id": str(response.id),
                "date": timezone.localtime(response.createAt).strftime("%d.%m.%Y %H:%M"),
                "task": response.assistant,
                "domain": domain_display,
                "model": response.model,
                "details": details,
                "result": response.html
            })
        
        return {
            "success": True,
            "data": data,
            "count": total_count,
            "error": None
        }
        
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "count": 0,
            "error": f"Ошибка при получении истории: {str(e)}"
        }