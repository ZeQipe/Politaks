"""
Функции создания данных товаров
Возвращают результат в едином формате
"""

import os
import random
from urllib.parse import urlparse
from django.utils import timezone
from ..models import Products, List, Satellite
from app.users.models import User
from app.config.models import Models, Assistant, Inputer, AssistantInputer


def extract_path_from_url(url):
    """Извлекает путь из URL (без домена и без начального /)"""
    if not url:
        return ""
    parsed = urlparse(url)
    path = parsed.path
    # Убираем начальный /
    if path.startswith('/'):
        path = path[1:]
    return path


def get_or_create_system_user():
    """Получает или создаёт системного пользователя для импорта данных"""
    system_user, created = User.objects.get_or_create(
        login='system_import',
        defaults={
            'firstName': 'System',
            'lastName': 'Import',
            'role': 'admin',
            'is_active': True,
            'is_superuser': False
        }
    )
    return system_user


def populate_products_from_data():
    """
    Заполняет БД данными из testData/products_data.py
    
    Порядок:
    1. Создаёт сателлиты (домены)
    2. Создаёт продукты из MAIN_LINK_BASE (пропуская существующие по title)
    3. Привязывает к каждому товару 6 случайных сателлит
    4. Создаёт связи из MAIN_RELATION_BASE
    
    Возвращает:
        dict: {
            'success': bool,
            'created_satellites': int,
            'skipped_satellites': int,
            'created_products': int,
            'skipped_products': int,
            'created_relations': int,
            'skipped_relations': int,
            'errors': list
        }
    """
    from testData.products_data import SATELLITES, MAIN_LINK_BASE, MAIN_RELATION_BASE
    
    result = {
        'success': True,
        'created_model': False,
        'created_satellites': 0,
        'skipped_satellites': 0,
        'created_products': 0,
        'skipped_products': 0,
        'created_relations': 0,
        'skipped_relations': 0,
        'satellite_links_added': 0,
        'errors': []
    }
    
    # Получаем системного пользователя
    system_user = get_or_create_system_user()
    
    # ========== 0. Создаём AI модель ==========
    try:
        existing_model = Models.objects.filter(name='GPT-4o').first()
        if not existing_model:
            openai_key = os.environ.get('OPENAI_API_KEY', '')
            if openai_key:
                model = Models(
                    name='GPT-4o',
                    url='https://api.openai.com/v1/chat/completions',
                    is_active=True
                )
                model.set_key(openai_key)
                model.save()
                result['created_model'] = True
            else:
                result['errors'].append("OPENAI_API_KEY не найден в переменных окружения")
    except Exception as e:
        result['errors'].append(f"Ошибка создания AI модели: {str(e)}")
    
    # ========== 1. Создаём сателлиты ==========
    satellites_list = []
    for title, domen in SATELLITES.items():
        try:
            existing = Satellite.objects.filter(domen=domen).first()
            if existing:
                satellites_list.append(existing)
                result['skipped_satellites'] += 1
                continue
            
            satellite = Satellite.objects.create(
                title=title,
                domen=domen
            )
            satellites_list.append(satellite)
            result['created_satellites'] += 1
            
        except Exception as e:
            result['errors'].append(f"Ошибка создания сателлита '{title}': {str(e)}")
    
    # ========== 2. Создаём продукты ==========
    products_cache = {}  # title -> product
    
    for title, base_link in MAIN_LINK_BASE.items():
        try:
            # Проверяем, существует ли уже
            existing = Products.objects.filter(title=title).first()
            if existing:
                products_cache[title] = existing
                result['skipped_products'] += 1
                continue
            
            # Извлекаем satelitLink (путь без домена и без начального /)
            satelit_link = extract_path_from_url(base_link)
            
            # Создаём продукт
            product = Products.objects.create(
                title=title,
                baseLink=base_link,
                satelitLink=satelit_link,
                description='',
                created_by=system_user
            )
            products_cache[title] = product
            result['created_products'] += 1
            
            # Привязываем 6 случайных сателлит
            if satellites_list:
                random_satellites = random.sample(
                    satellites_list, 
                    min(6, len(satellites_list))
                )
                product.satelitDomens.add(*random_satellites)
                result['satellite_links_added'] += len(random_satellites)
            
        except Exception as e:
            result['errors'].append(f"Ошибка создания продукта '{title}': {str(e)}")
    
    # ========== 3. Создаём связи между товарами ==========
    for main_product_title, related_titles in MAIN_RELATION_BASE.items():
        # Ищем основной продукт
        main_product = products_cache.get(main_product_title)
        if not main_product:
            main_product = Products.objects.filter(title=main_product_title).first()
        
        if not main_product:
            result['errors'].append(f"Товар не найден: '{main_product_title}'")
            continue
        
        # Обрабатываем связанные продукты
        for related_title in related_titles:
            try:
                # Ищем связанный продукт
                related_product = products_cache.get(related_title)
                if not related_product:
                    related_product = Products.objects.filter(title=related_title).first()
                
                if not related_product:
                    result['errors'].append(f"Связанный товар не найден: '{related_title}'")
                    continue
                
                # Проверяем, существует ли связь
                existing_relation = List.objects.filter(
                    product=main_product,
                    related_product=related_product
                ).first()
                
                if existing_relation:
                    result['skipped_relations'] += 1
                    continue
                
                # Создаём связь
                List.objects.create(
                    product=main_product,
                    related_product=related_product,
                    description=''
                )
                result['created_relations'] += 1
                
            except Exception as e:
                result['errors'].append(
                    f"Ошибка создания связи '{main_product_title}' -> '{related_title}': {str(e)}"
                )
    
    if result['errors']:
        result['success'] = len(result['errors']) < 10  # Частичный успех если мало ошибок
    
    return result


def populate_inputers_from_data():
    """
    Заполняет БД инпутерами из testData/inputers_data.py
    
    Возвращает:
        dict: {
            'success': bool,
            'created_inputers': int,
            'skipped_inputers': int,
            'errors': list
        }
    """
    from testData.inputers_data import INPUTERS_DATA
    
    result = {
        'success': True,
        'created_inputers': 0,
        'skipped_inputers': 0,
        'errors': []
    }
    
    for name, data in INPUTERS_DATA.items():
        try:
            # Проверяем, существует ли уже
            existing = Inputer.objects.filter(name=name).first()
            if existing:
                result['skipped_inputers'] += 1
                continue
            
            # Создаём инпутер
            Inputer.objects.create(
                name=name,
                label=data['label'],
                type=data['type'],
                size=data['size'],
                placement=data['placement'],
                type_select=data['type_select'],
                select_search=data['select_search'],
                multi_select=data['multi_select'],
            )
            result['created_inputers'] += 1
            
        except Exception as e:
            result['errors'].append(f"Ошибка создания инпутера '{name}': {str(e)}")
    
    if result['errors']:
        result['success'] = len(result['errors']) < 5
    
    return result


def populate_assistants_from_data():
    """
    Заполняет БД ассистентами из testData/assistants_data.py
    
    Логика:
    1. Сначала создаёт все инпутеры
    2. Создаёт ассистентов из ASSISTANTS_DATA (пропуская существующие по key_title)
    3. Создаёт связи AssistantInputer с порядком
    
    Возвращает:
        dict: {
            'success': bool,
            'created_inputers': int,
            'skipped_inputers': int,
            'created_assistants': int,
            'skipped_assistants': int,
            'created_links': int,
            'errors': list
        }
    """
    from testData.assistants_data import ASSISTANTS_DATA
    from testData.inputers_data import ASSISTANT_INPUTERS
    
    # Сначала создаём инпутеры
    inputers_result = populate_inputers_from_data()
    
    result = {
        'success': True,
        'created_inputers': inputers_result['created_inputers'],
        'skipped_inputers': inputers_result['skipped_inputers'],
        'created_assistants': 0,
        'skipped_assistants': 0,
        'created_links': 0,
        'errors': inputers_result['errors'].copy()
    }
    
    for key_title, data in ASSISTANTS_DATA.items():
        try:
            # Проверяем, существует ли уже
            existing = Assistant.objects.filter(key_title=key_title).first()
            if existing:
                result['skipped_assistants'] += 1
                continue
            
            # Создаём ассистента
            assistant = Assistant.objects.create(
                key_title=key_title,
                title=data['title'],
                instruction=data['instruction'],
                default_sheets_id=data['default_sheets_id'],
                maks_token=None,
                temperatures=None
            )
            result['created_assistants'] += 1
            
            # Создаём связи с инпутерами
            inputer_names = ASSISTANT_INPUTERS.get(key_title, [])
            for order, inputer_name in enumerate(inputer_names):
                try:
                    inputer = Inputer.objects.filter(name=inputer_name).first()
                    if inputer:
                        # Проверяем, нет ли уже такой связи
                        existing_link = AssistantInputer.objects.filter(
                            assistant=assistant,
                            inputer=inputer
                        ).first()
                        if not existing_link:
                            AssistantInputer.objects.create(
                                assistant=assistant,
                                inputer=inputer,
                                required='required',
                                order=order
                            )
                            result['created_links'] += 1
                except Exception as e:
                    result['errors'].append(f"Ошибка связи '{key_title}' - '{inputer_name}': {str(e)}")
            
        except Exception as e:
            result['errors'].append(f"Ошибка создания ассистента '{key_title}': {str(e)}")
    
    if result['errors']:
        result['success'] = len(result['errors']) < 5
    
    return result
