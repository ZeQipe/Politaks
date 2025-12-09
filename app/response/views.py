import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .interface.set import save_response


@csrf_exempt
@require_http_methods(["POST"])
def save_excel_response(request):
    """
    POST /api/response/save
    Сохранение ответа от микросервиса Sheets
    
    Принимает JSON:
    {
        "parametrs": "...",
        "domen": "main" или "https://...",  // domain_url
        "html": "<p>...</p>",
        "user": "1",                        // user_id как строка
        "model": "gpt-4.1",
        "assistant": "description"          // key_title
    }
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Некорректный JSON'
        }, status=400)
    
    # Получаем поля (названия как от Sheets сервиса)
    parametrs = data.get('parametrs', '')
    domen_url = data.get('domen', 'main')        # domain_url
    html = data.get('html', '')
    user_id_str = data.get('user', '')           # user_id как строка
    model = data.get('model', '')
    assistant_key = data.get('assistant', '')    # key_title
    
    # Преобразуем user_id в int
    user_id = None
    if user_id_str:
        try:
            user_id = int(user_id_str)
        except (ValueError, TypeError):
            user_id = None
    
    # Валидация обязательных полей
    if not html:
        return JsonResponse({
            'success': False,
            'error': 'Параметр html обязателен'
        }, status=400)
    
    if not model:
        return JsonResponse({
            'success': False,
            'error': 'Параметр model обязателен'
        }, status=400)
    
    if not assistant_key:
        return JsonResponse({
            'success': False,
            'error': 'Параметр assistant обязателен'
        }, status=400)
    
    result = save_response(
        parametrs=parametrs,
        domen_url=domen_url,
        html=html,
        user_id=user_id,
        model=model,
        assistant_key=assistant_key,
        source='excel'
    )
    
    if result['success']:
        return JsonResponse({
            'success': True,
            'data': result['data']
        }, status=201)
    else:
        return JsonResponse({
            'success': False,
            'error': result['error']
        }, status=500)
