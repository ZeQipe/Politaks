"""
Парсер CSV файлов для заполнения БД товарами и связями
"""

import csv
import os
from django.conf import settings


def get_csv_path(filename):
    """Получает полный путь к CSV файлу"""
    path = os.path.join(settings.BASE_DIR, 'testData', 'csv', filename)
    return path


def check_csv_files():
    """Проверяет наличие CSV файлов и возвращает информацию"""
    result = {
        'base_dir': str(settings.BASE_DIR),
        'products_csv': {},
        'relations_csv': {}
    }
    
    products_path = get_csv_path('product.csv')
    relations_path = get_csv_path('link_product.csv')
    
    result['products_csv']['path'] = products_path
    result['products_csv']['exists'] = os.path.exists(products_path)
    
    result['relations_csv']['path'] = relations_path
    result['relations_csv']['exists'] = os.path.exists(relations_path)
    
    # Диагностика: размер файлов и первые строки
    if result['products_csv']['exists']:
        try:
            result['products_csv']['size'] = os.path.getsize(products_path)
            with open(products_path, 'r', encoding='utf-8-sig') as f:
                result['products_csv']['first_lines'] = [f.readline().strip() for _ in range(3)]
        except Exception as e:
            result['products_csv']['read_error'] = str(e)
    
    if result['relations_csv']['exists']:
        try:
            result['relations_csv']['size'] = os.path.getsize(relations_path)
            with open(relations_path, 'r', encoding='utf-8-sig') as f:
                result['relations_csv']['first_lines'] = [f.readline().strip() for _ in range(3)]
        except Exception as e:
            result['relations_csv']['read_error'] = str(e)
    
    return result


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
        # utf-8-sig обрабатывает BOM автоматически
        with open(csv_path, 'r', encoding='utf-8-sig') as file:
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
    except Exception as e:
        # Логируем ошибку для отладки
        print(f"CSV parse error (products): {e}")
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
        # utf-8-sig обрабатывает BOM автоматически
        with open(csv_path, 'r', encoding='utf-8-sig') as file:
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
    except Exception as e:
        # Логируем ошибку для отладки
        print(f"CSV parse error (relations): {e}")
        return []
    
    return relations

