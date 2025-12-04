import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .interface.get import get_filters_for_generation, get_filters_for_history, get_form_config
from .interface.set import generate_content


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
        user=user
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
