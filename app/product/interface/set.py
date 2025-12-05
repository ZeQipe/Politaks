"""
Функции создания данных товаров
Возвращают результат в едином формате
"""

from urllib.parse import urlparse
from django.utils import timezone
from ..models import Products, List, Satellite
from app.users.models import User


def extract_path_from_url(url):
    """Извлекает путь из URL (без домена)"""
    if not url:
        return ""
    parsed = urlparse(url)
    return parsed.path


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
    
    Логика:
    1. Создаёт продукты из MAIN_LINK_BASE (пропуская существующие по title)
    2. Создаёт связи из MAIN_RELATION_BASE
    
    Возвращает:
        dict: {
            'success': bool,
            'created_products': int,
            'skipped_products': int,
            'created_relations': int,
            'skipped_relations': int,
            'errors': list
        }
    """
    from testData.products_data import MAIN_LINK_BASE, MAIN_RELATION_BASE
    
    result = {
        'success': True,
        'created_products': 0,
        'skipped_products': 0,
        'created_relations': 0,
        'skipped_relations': 0,
        'errors': []
    }
    
    # Получаем системного пользователя
    system_user = get_or_create_system_user()
    
    # Словарь для быстрого поиска продуктов по названию
    products_cache = {}
    
    # 1. Создаём продукты из MAIN_LINK_BASE
    for title, base_link in MAIN_LINK_BASE.items():
        try:
            # Проверяем, существует ли уже
            existing = Products.objects.filter(title=title).first()
            if existing:
                products_cache[title] = existing
                result['skipped_products'] += 1
                continue
            
            # Извлекаем satelitLink (путь без домена)
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
            
        except Exception as e:
            result['errors'].append(f"Ошибка создания продукта '{title}': {str(e)}")
    
    # 2. Создаём связи из MAIN_RELATION_BASE
    for main_product_title, related_products in MAIN_RELATION_BASE.items():
        # Ищем или создаём основной продукт (тот, с которым связаны)
        main_product = products_cache.get(main_product_title)
        if not main_product:
            main_product = Products.objects.filter(title=main_product_title).first()
        
        if not main_product:
            # Создаём продукт, если его нет
            try:
                main_product = Products.objects.create(
                    title=main_product_title,
                    baseLink='',
                    satelitLink='',
                    description='',
                    created_by=system_user
                )
                products_cache[main_product_title] = main_product
                result['created_products'] += 1
            except Exception as e:
                result['errors'].append(f"Ошибка создания основного продукта '{main_product_title}': {str(e)}")
                continue
        
        # Обрабатываем связанные продукты
        for related_title, relation_data in related_products.items():
            try:
                # Ищем или создаём связанный продукт
                related_product = products_cache.get(related_title)
                if not related_product:
                    related_product = Products.objects.filter(title=related_title).first()
                
                if not related_product:
                    # Создаём продукт, если его нет
                    relation_link = relation_data.get('link', '')
                    satelit_link = extract_path_from_url(relation_link) if relation_link else ''
                    
                    related_product = Products.objects.create(
                        title=related_title,
                        baseLink=relation_link,
                        satelitLink=satelit_link,
                        description='',
                        created_by=system_user
                    )
                    products_cache[related_title] = related_product
                    result['created_products'] += 1
                
                # Проверяем, существует ли связь
                existing_relation = List.objects.filter(
                    product=main_product,
                    related_product=related_product
                ).first()
                
                if existing_relation:
                    result['skipped_relations'] += 1
                    continue
                
                # Создаём связь
                # main_product - товар, С КОТОРЫМ связаны
                # related_product - связанный товар
                List.objects.create(
                    product=main_product,
                    related_product=related_product,
                    description=relation_data.get('description', '')
                )
                result['created_relations'] += 1
                
            except Exception as e:
                result['errors'].append(
                    f"Ошибка создания связи '{main_product_title}' -> '{related_title}': {str(e)}"
                )
    
    if result['errors']:
        result['success'] = len(result['errors']) < 5  # Частичный успех если мало ошибок
    
    return result
