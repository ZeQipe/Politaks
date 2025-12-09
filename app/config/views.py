import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .interface.get import get_filters_for_generation, get_filters_for_history, get_form_config, get_history
from .interface.set import generate_content, generate_excel_content


@require_http_methods(["GET"])
def generation_filters(request):
    """
    GET /api/generation/filters
    Фильтры для страницы генерации
    """
    result = get_filters_for_generation()
    
    if result['success']:
        return JsonResponse(result['data'], status=200)
    else:
        return JsonResponse({
            'success': False,
            'error': result['error']
        }, status=500)


@require_http_methods(["GET"])
def history_filters(request):
    """
    GET /api/history/filters
    Фильтры для страницы истории
    """
    result = get_filters_for_history()
    
    if result['success']:
        return JsonResponse(result['data'], status=200)
    else:
        return JsonResponse({
            'success': False,
            'error': result['error']
        }, status=500)


@require_http_methods(["GET"])
def history(request):
    """
    GET /api/history?count=10&offset=0&taskId=...&modelId=...&domainId=...
    Получение истории генераций
    """
    # Получаем параметры
    count = request.GET.get('count', '10')
    offset = request.GET.get('offset', '0')
    task_id = request.GET.get('taskId')
    model_id = request.GET.get('modelId')
    domain_id = request.GET.get('domainId')
    
    # Преобразуем count и offset в int
    try:
        count = int(count)
        offset = int(offset)
    except ValueError:
        return JsonResponse({
            'status': 'error',
            'data': [],
            'count': 0
        }, status=400)
    
    result = get_history(
        count=count,
        offset=offset,
        task_id=task_id,
        model_id=model_id,
        domain_id=domain_id
    )
    
    if result['success']:
        return JsonResponse({
            'status': 'success',
            'data': result['data'],
            'count': result['count']
        }, status=200)
    else:
        return JsonResponse({
            'status': 'error',
            'data': [],
            'count': 0
        }, status=500)


@require_http_methods(["GET"])
def form_config(request):
    """
    GET /api/generation/form-config?taskId=...&domainId=...
    Конфигурация формы для генерации
    """
    task_id = request.GET.get('taskId')
    domain_id = request.GET.get('domainId', 'main')
    
    if not task_id:
        return JsonResponse({
            'success': False,
            'error': 'Параметр taskId обязателен'
        }, status=400)
    
    result = get_form_config(task_id=task_id, domain_id=domain_id)
    
    if result['success']:
        return JsonResponse(result['data'], safe=False, status=200)
    else:
        return JsonResponse({
            'success': False,
            'error': result['error']
        }, status=404)


@csrf_exempt
@require_http_methods(["POST"])
def generate(request):
    """
    POST /api/generation/generate
    Генерация контента
    
    Принимает:
    - application/json: {"filters": {...}, "fields": [...]}
    - multipart/form-data: filters[taskId], filters[modelId], filters[domainId], fields[0][name], fields[0][value], photo1, photo2
    """
    content_type = request.content_type or ''
    
    # Определяем тип контента и извлекаем данные
    if 'multipart/form-data' in content_type:
        # FormData (для файлов)
        data, files = _parse_form_data(request)
    else:
        # JSON
        try:
            data = json.loads(request.body)
            files = None
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Некорректный JSON'
            }, status=400)
    
    # Получаем filters
    filters = data.get('filters', {})
    task_id = filters.get('taskId')
    model_id = filters.get('modelId')
    domain_id = filters.get('domainId', 'main')
    
    # Получаем fields
    fields = data.get('fields', [])
    
    # Валидация обязательных параметров
    if not task_id:
        return JsonResponse({
            'success': False,
            'error': 'Параметр filters.taskId обязателен'
        }, status=400)
    
    if not model_id:
        return JsonResponse({
            'success': False,
            'error': 'Параметр filters.modelId обязателен'
        }, status=400)
    
    # Получаем пользователя (пока anonymous, потом можно из auth)
    user = "anonymous"
    if hasattr(request, 'user') and request.user.is_authenticated:
        user = request.user.login
    
    result = generate_content(
        task_id=task_id,
        model_id=model_id,
        domain_id=domain_id,
        fields=fields,
        user=user,
        files=files
    )
    
    if result['success']:
        return JsonResponse({
            'success': True,
            'data': result['data']
        }, status=200)
    else:
        return JsonResponse({
            'success': False,
            'error': result['error']
        }, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def generate_excel(request):
    """
    POST /api/generation/generate-excel
    Генерация контента из Excel файла
    
    Принимает JSON:
    {
        "filters": {"taskId": "...", "modelId": "..."},
        "excelLink": "https://...",
        "range": {"from": 0, "to": 0}
    }
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Некорректный JSON'
        }, status=400)
    
    # Получаем filters
    filters = data.get('filters', {})
    task_id = filters.get('taskId')
    model_id = filters.get('modelId')
    
    # Получаем excel link
    excel_link = data.get('excelLink')
    
    # Получаем range
    range_data = data.get('range', {})
    range_from = range_data.get('from', 0)
    range_to = range_data.get('to', 0)
    
    # Валидация обязательных параметров
    if not task_id:
        return JsonResponse({
            'success': False,
            'error': 'Параметр filters.taskId обязателен'
        }, status=400)
    
    if not model_id:
        return JsonResponse({
            'success': False,
            'error': 'Параметр filters.modelId обязателен'
        }, status=400)
    
    if not excel_link:
        return JsonResponse({
            'success': False,
            'error': 'Параметр excelLink обязателен'
        }, status=400)
    
    result = generate_excel_content(
        task_id=task_id,
        model_id=model_id,
        excel_link=excel_link,
        range_from=range_from,
        range_to=range_to
    )
    
    if result['success']:
        return JsonResponse({
            'success': True,
            'data': result['data']
        }, status=200)
    else:
        return JsonResponse({
            'success': False,
            'error': result['error']
        }, status=400)


def _parse_form_data(request) -> tuple[dict, dict]:
    """
    Парсит multipart/form-data запрос
    
    Формат ожидаемых полей:
    - filters[taskId]: string
    - filters[modelId]: string
    - filters[domainId]: string
    - fields[0][name]: string
    - fields[0][value]: string | JSON-массив (для multiple select)
    - fields[1][name]: string
    - fields[1][value]: string | JSON-массив
    - photo1: File
    - photo2: File
    
    Примечание:
        Если value является JSON-строкой с массивом (например '["val1", "val2"]'),
        он автоматически парсится в list.
    
    Returns:
        tuple: (data_dict, files_dict)
    """
    data = {
        'filters': {},
        'fields': []
    }
    files = {}
    
    # Парсим filters
    for key in ['taskId', 'modelId', 'domainId']:
        form_key = f'filters[{key}]'
        if form_key in request.POST:
            data['filters'][key] = request.POST[form_key]
    
    # Парсим fields (массив объектов)
    # Собираем все поля вида fields[N][name] и fields[N][value]
    field_indices = set()
    for key in request.POST.keys():
        if key.startswith('fields[') and '][' in key:
            # Извлекаем индекс: fields[0][name] -> 0
            try:
                idx = int(key.split('[')[1].split(']')[0])
                field_indices.add(idx)
            except (ValueError, IndexError):
                continue
    
    # Сортируем индексы и собираем поля
    for idx in sorted(field_indices):
        name_key = f'fields[{idx}][name]'
        value_key = f'fields[{idx}][value]'
        
        name = request.POST.get(name_key, '')
        value = request.POST.get(value_key, '')
        
        # Проверяем, является ли value JSON-строкой с массивом (для multiple select)
        if value and value.startswith('[') and value.endswith(']'):
            try:
                parsed_value = json.loads(value)
                if isinstance(parsed_value, list):
                    value = parsed_value
            except json.JSONDecodeError:
                pass  # Оставляем как строку
        
        if name:
            data['fields'].append({
                'name': name,
                'value': value
            })
    
    # Парсим файлы
    for file_key in ['photo1', 'photo2']:
        if file_key in request.FILES:
            uploaded_file = request.FILES[file_key]
            files[file_key] = uploaded_file.read()
    
    return data, files if files else None
