"""
Парсер CSV файлов для заполнения БД товарами и связями
"""

import csv
import os
from django.conf import settings


def get_csv_path(filename):
    """Получает полный путь к CSV файлу"""
    return os.path.join(settings.BASE_DIR, 'testData', 'csv', filename)


def parse_products_csv():
    """
    Парсит product.csv и возвращает список товаров
    
    Формат CSV: name, main_link, sub_link
    - name -> title
    - main_link -> baseLink
    - sub_link -> satelitLink (если пусто - None)
    
    Возвращает:
        list[dict]: [{'title': str, 'baseLink': str, 'satelitLink': str|None}, ...]
    """
    products = []
    csv_path = get_csv_path('product.csv')
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                name = row.get('name', '').strip().strip('"')
                main_link = row.get('main_link', '').strip()
                sub_link = row.get('sub_link', '').strip()
                
                # Пропускаем строки без названия
                if not name:
                    continue
                
                products.append({
                    'title': name,
                    'baseLink': main_link if main_link else None,
                    'satelitLink': sub_link if sub_link else None,
                })
    
    except FileNotFoundError:
        return []
    except Exception:
        return []
    
    return products


def parse_relations_csv():
    """
    Парсит link_product.csv и возвращает список связей
    
    Формат CSV: main_name, relation_name, relation_description
    - main_name - товар, к которому привязываем (если пусто - используем предыдущий)
    - relation_name - товар, который привязываем
    - relation_description - описание связи (если пусто - пустая строка)
    
    Возвращает:
        list[dict]: [{'main_name': str, 'relation_name': str, 'description': str}, ...]
    """
    relations = []
    csv_path = get_csv_path('link_product.csv')
    current_main_name = None
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                main_name = row.get('main_name', '').strip()
                relation_name = row.get('relation_name', '').strip()
                description = row.get('relation_description', '').strip()
                
                # Пропускаем строки без связанного товара
                if not relation_name:
                    continue
                
                # Если main_name пустой - используем предыдущий
                if main_name:
                    current_main_name = main_name
                
                # Если нет текущего main_name - пропускаем
                if not current_main_name:
                    continue
                
                relations.append({
                    'main_name': current_main_name,
                    'relation_name': relation_name,
                    'description': description if description else '',
                })
    
    except FileNotFoundError:
        return []
    except Exception:
        return []
    
    return relations

