from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .interface.get import get_related_products_by_domain
import json


@csrf_exempt
@require_http_methods(["GET", "POST"])
def get_product_links(request):
    """
    Получение связанных товаров с ссылками
    
    Входные параметры:
        - domain_title: str | None (название домена)
        - product_name: str (название товара)
    
    Возвращает:
        JSON с информацией о связанных товарах
    """
    try:
        # Получаем параметры в зависимости от метода запроса
        if request.method == 'POST':
            data = json.loads(request.body)
            domain_title = data.get('domain_title')
            product_name = data.get('product_name')
        else:  # GET
            domain_title = request.GET.get('domain_title')
            product_name = request.GET.get('product_name')
        
        # Валидация обязательных параметров
        if not product_name:
            return JsonResponse({
                'success': False,
                'error': 'Параметр product_name обязателен'
            }, status=400)
        
        # Получаем данные через interface
        result = get_related_products_by_domain(
            product_name=product_name,
            domain_title=domain_title
        )
        
        # Возвращаем результат
        if result['success']:
            return JsonResponse(result['data'], status=200)
        else:
            return JsonResponse({
                'success': False,
                'error': result['error']
            }, status=404)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Некорректный JSON'
        }, status=400)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Внутренняя ошибка сервера: {str(e)}'
        }, status=500)
