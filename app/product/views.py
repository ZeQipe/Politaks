from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .interface.get import get_related_products_by_domain, get_product_link_by_domain
from .interface.set import populate_products_from_data, populate_assistants_from_data
import json

# Пароль для доступа к роуту заполнения БД
POPULATE_PASSWORD = "ai_zeqipe"


@csrf_exempt
@require_http_methods(["GET", "POST"])
def get_product_links(request):
    """
    Получение связанных товаров с ссылками
    
    Входные параметры:
        - domain_url: str | None (URL домена)
        - product_name: str (название товара)
    
    Возвращает:
        JSON с информацией о связанных товарах
    """
    try:
        # Получаем параметры в зависимости от метода запроса
        if request.method == 'POST':
            data = json.loads(request.body)
            domain_url = data.get('domain_url')
            product_name = data.get('product_name')
        else:  # GET
            domain_url = request.GET.get('domain_url')
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
            domain_url=domain_url
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


@csrf_exempt
@require_http_methods(["GET", "POST"])
def get_product_link(request):
    """
    Получение ссылки на товар
    
    Входные параметры:
        - domain_url: str | None (URL домена, None или "main" = базовые ссылки)
        - product_name: str (название товара или "_all" для всех)
    
    Возвращает:
        - Для одного товара: строка ссылки
        - Для "_all": словарь {название: ссылка}
    """
    try:
        # Получаем параметры в зависимости от метода запроса
        if request.method == 'POST':
            data = json.loads(request.body)
            domain_url = data.get('domain_url')
            product_name = data.get('product_name')
        else:  # GET
            domain_url = request.GET.get('domain_url')
            product_name = request.GET.get('product_name')
        
        # Валидация обязательных параметров
        if not product_name:
            return JsonResponse({
                'success': False,
                'error': 'Параметр product_name обязателен'
            }, status=400)
        
        # Получаем данные через interface
        result = get_product_link_by_domain(
            product_name=product_name,
            domain_url=domain_url
        )
        
        # Возвращаем результат
        if result['success']:
            return JsonResponse({'data': result['data']}, status=200)
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


@csrf_exempt
@require_http_methods(["GET", "POST"])
def populate_database(request):
    """
    Заполнение БД тестовыми данными из testData/products_data.py
    
    Query параметры:
        - password: str (обязательный, должен быть "ai_zeqipe")
    
    Возвращает:
        JSON с информацией о результате заполнения
    """
    try:
        # Получаем пароль из query параметров
        password = request.GET.get('password') or request.POST.get('password')
        
        # Проверка пароля
        if not password:
            return JsonResponse({
                'success': False,
                'error': 'Параметр password обязателен'
            }, status=400)
        
        if password != POPULATE_PASSWORD:
            return JsonResponse({
                'success': False,
                'error': 'Неверный пароль'
            }, status=403)
        
        # Запускаем заполнение БД продуктами
        products_result = populate_products_from_data()
        
        # Запускаем заполнение БД ассистентами
        assistants_result = populate_assistants_from_data()
        
        # Объединяем результаты
        all_errors = (products_result['errors'] or []) + (assistants_result['errors'] or [])
        overall_success = products_result['success'] and assistants_result['success']
        
        return JsonResponse({
            'success': overall_success,
            'message': 'Заполнение БД завершено',
            'statistics': {
                'products': {
                    'created': products_result['created_products'],
                    'skipped': products_result['skipped_products'],
                },
                'relations': {
                    'created': products_result['created_relations'],
                    'skipped': products_result['skipped_relations'],
                },
                'inputers': {
                    'created': assistants_result['created_inputers'],
                    'skipped': assistants_result['skipped_inputers'],
                },
                'assistants': {
                    'created': assistants_result['created_assistants'],
                    'skipped': assistants_result['skipped_assistants'],
                },
                'assistant_inputer_links': {
                    'created': assistants_result['created_links'],
                }
            },
            'errors': all_errors if all_errors else None
        }, status=200 if overall_success else 207)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Внутренняя ошибка сервера: {str(e)}'
        }, status=500)
