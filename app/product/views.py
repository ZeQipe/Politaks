from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .interface.get import get_related_products_by_domain, get_product_link_by_domain
from .interface.set import populate_products_from_data, populate_assistants_from_data, populate_products_from_csv, populate_base_config
import json

# Пароль для доступа к роуту заполнения БД
POPULATE_PASSWORD = "ai_zeqipe"


@csrf_exempt
@require_http_methods(["GET", "POST"])
def get_product_links(request):
    """
    Получение связанных товаров с ссылками
    
    Входные параметры:
        - domain_url/domain_title: str | None (title или URL домена)
        - product_name: list[str] (список названий товаров)
    
    Возвращает:
        dict: {название: {связанный_товар: {link, description}}}
    """
    try:
        # Получаем параметры в зависимости от метода запроса
        if request.method == 'POST':
            data = json.loads(request.body)
            # Принимаем и domain_url, и domain_title
            domain_url = data.get('domain_url') or data.get('domain_title')
            product_names = data.get('product_name', [])
        else:  # GET
            domain_url = request.GET.get('domain_url') or request.GET.get('domain_title')
            # Для GET запроса product_name может быть передан несколько раз
            product_names = request.GET.getlist('product_name')
        
        # Валидация обязательных параметров
        if not product_names:
            return JsonResponse({
                'success': False,
                'error': 'Параметр product_name обязателен'
            }, status=400)
        
        # Получаем данные через interface
        result = get_related_products_by_domain(
            product_names=product_names,
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
    Получение ссылок на товары
    
    Входные параметры:
        - domain_url/domain_title: str | None (title или URL домена, None/"main" = базовые ссылки)
        - product_name: list[str] (список названий товаров)
    
    Возвращает:
        dict: {название: ссылка}
    """
    try:
        # Получаем параметры в зависимости от метода запроса
        if request.method == 'POST':
            data = json.loads(request.body)
            # Принимаем и domain_url, и domain_title
            domain_url = data.get('domain_url') or data.get('domain_title')
            product_names = data.get('product_name', [])
        else:  # GET
            domain_url = request.GET.get('domain_url') or request.GET.get('domain_title')
            # Для GET запроса product_name может быть передан несколько раз
            product_names = request.GET.getlist('product_name')
        
        # Валидация обязательных параметров
        if not product_names:
            return JsonResponse({
                'success': False,
                'error': 'Параметр product_name обязателен'
            }, status=400)
        
        # Получаем данные через interface
        result = get_product_link_by_domain(
            product_names=product_names,
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


@csrf_exempt
@require_http_methods(["GET", "POST"])
def populate_from_csv(request):
    """
    Заполнение БД данными из CSV файлов (testData/csv/)
    
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
        
        # Запускаем заполнение БД из CSV
        csv_result = populate_products_from_csv()
        
        return JsonResponse({
            'success': csv_result['success'],
            'message': 'Заполнение БД из CSV завершено',
            'statistics': {
                'products': {
                    'created': csv_result['created_products'],
                    'skipped': csv_result['skipped_products'],
                },
                'satellite_links_added': csv_result['satellite_links_added'],
                'relations': {
                    'created': csv_result['created_relations'],
                    'skipped': csv_result['skipped_relations'],
                },
            },
            'errors': csv_result['errors'] if csv_result['errors'] else None
        }, status=200 if csv_result['success'] else 207)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Внутренняя ошибка сервера: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def populate_config(request):
    """
    Заполнение БД базовой конфигурацией:
    - Домены сателлитов
    - AI модель GPT-4o
    - Инпутеры
    - Ассистенты
    - Связи ассистентов с инпутерами
    
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
        
        # Запускаем заполнение базовой конфигурации
        config_result = populate_base_config()
        
        return JsonResponse({
            'success': config_result['success'],
            'message': 'Заполнение базовой конфигурации завершено',
            'statistics': {
                'model': {
                    'created': config_result['created_model'],
                },
                'satellites': {
                    'created': config_result['created_satellites'],
                    'skipped': config_result['skipped_satellites'],
                },
                'inputers': {
                    'created': config_result['created_inputers'],
                    'skipped': config_result['skipped_inputers'],
                },
                'assistants': {
                    'created': config_result['created_assistants'],
                    'skipped': config_result['skipped_assistants'],
                },
                'assistant_inputer_links': {
                    'created': config_result['created_assistant_inputer_links'],
                },
            },
            'errors': config_result['errors'] if config_result['errors'] else None
        }, status=200 if config_result['success'] else 207)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Внутренняя ошибка сервера: {str(e)}'
        }, status=500)
