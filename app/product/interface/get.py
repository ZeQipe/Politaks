"""
Функции получения данных товаров
Возвращают данные в едином формате
"""
from ..models import Products, Satellite, List


def get_related_products_by_domain(product_name: str, domain_url: str = None):
    """
    Получение связанных товаров с учетом домена
    
    Args:
        product_name: Название товара
        domain_url: URL домена (None = базовые ссылки)
    
    Returns:
        dict: {
            "success": bool,
            "data": dict или None,
            "error": str или None
        }
    """
    try:
        # Шаг 1: Находим основной товар по названию
        try:
            product = Products.objects.get(title=product_name)
        except Products.DoesNotExist:
            return {
                "success": False,
                "data": None,
                "error": f"Товар '{product_name}' не найден"
            }
        
        # Шаг 2: Определяем домен по URL
        satellite = None
        if domain_url:
            try:
                satellite = Satellite.objects.get(domen=domain_url)
            except Satellite.DoesNotExist:
                return {
                    "success": False,
                    "data": None,
                    "error": f"Домен '{domain_url}' не найден"
                }
        
        # Шаг 3: Получаем все связи текущего товара
        relations = List.objects.filter(product=product).select_related('related_product')
        
        # Шаг 4: Фильтруем связанные товары по логике
        result = {}
        
        for relation in relations:
            related_product = relation.related_product
            
            # Фильтрация в зависимости от наличия домена
            if domain_url is None:
                # Если домен None - нужны товары с baseLink
                if not related_product.baseLink:
                    continue
                
                link = related_product.baseLink
                
            else:
                # Если домен есть - проверяем, есть ли у связанного товара этот сателлит
                if not satellite in related_product.satelitDomens.all():
                    continue
                
                # Проверяем наличие satelitLink
                if not related_product.satelitLink:
                    continue
                
                # Склеиваем домен + satelitLink
                link = _join_url(satellite.domen, related_product.satelitLink)
            
            # Формируем результат
            result[related_product.title] = {
                "link": link,
                "description": relation.description or ""
            }
        
        # Шаг 5: Формируем итоговый ответ
        return {
            "success": True,
            "data": {
                product_name: result
            },
            "error": None
        }
        
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": f"Ошибка при получении данных: {str(e)}"
        }


def get_product_link_by_domain(product_name: str, domain_url: str = None):
    """
    Получение ссылки на товар с учетом домена
    
    Args:
        product_name: Название товара или "_all" для всех товаров
        domain_url: URL домена (None = базовые ссылки)
    
    Returns:
        dict: {
            "success": bool,
            "data": str или dict,
            "error": str или None
        }
    """
    try:
        # Если запрашиваются все товары
        if product_name == "_all":
            return _get_all_product_links(domain_url)
        
        # Шаг 1: Находим товар по названию
        try:
            product = Products.objects.get(title=product_name)
        except Products.DoesNotExist:
            return {
                "success": False,
                "data": None,
                "error": f"Товар '{product_name}' не найден"
            }
        
        # Шаг 2: Определяем ссылку в зависимости от домена
        if domain_url is None or domain_url == "main":
            # Базовая ссылка
            link = product.baseLink or ""
        else:
            # Ссылка для сателлита
            try:
                satellite = Satellite.objects.get(domen=domain_url)
            except Satellite.DoesNotExist:
                return {
                    "success": False,
                    "data": None,
                    "error": f"Домен '{domain_url}' не найден"
                }
            
            # Проверяем, есть ли товар на этом сателлите
            if satellite not in product.satelitDomens.all():
                return {
                    "success": True,
                    "data": "",
                    "error": None
                }
            
            # Склеиваем домен + satelitLink
            if product.satelitLink:
                link = _join_url(satellite.domen, product.satelitLink)
            else:
                link = ""
        
        return {
            "success": True,
            "data": link,
            "error": None
        }
        
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": f"Ошибка при получении ссылки: {str(e)}"
        }


def _get_all_product_links(domain_url: str = None):
    """
    Получение всех ссылок на товары
    
    Args:
        domain_url: URL домена (None = базовые ссылки)
    
    Returns:
        dict: {"success": bool, "data": dict, "error": str}
    """
    try:
        result = {}
        
        if domain_url is None or domain_url == "main":
            # Базовые ссылки - все товары с baseLink
            products = Products.objects.filter(baseLink__isnull=False).exclude(baseLink='')
            for product in products:
                result[product.title] = product.baseLink
        else:
            # Ссылки для сателлита
            try:
                satellite = Satellite.objects.get(domen=domain_url)
            except Satellite.DoesNotExist:
                return {
                    "success": False,
                    "data": None,
                    "error": f"Домен '{domain_url}' не найден"
                }
            
            # Товары этого сателлита с satelitLink
            products = satellite.products.filter(satelitLink__isnull=False).exclude(satelitLink='')
            for product in products:
                result[product.title] = _join_url(satellite.domen, product.satelitLink)
        
        return {
            "success": True,
            "data": result,
            "error": None
        }
        
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": f"Ошибка при получении ссылок: {str(e)}"
        }


def _join_url(domain: str, path: str) -> str:
    """
    Склеивает домен и путь, убирая дублирующийся слеш
    
    Args:
        domain: Домен (например, "https://example.com/")
        path: Путь (например, "/product")
    
    Returns:
        str: Склеенный URL
    """
    # Убираем дублирующийся слеш
    if domain.endswith('/') and path.startswith('/'):
        return domain + path[1:]
    
    # Если нет слеша между ними, добавляем
    if not domain.endswith('/') and not path.startswith('/'):
        return domain + '/' + path
    
    # Иначе просто склеиваем
    return domain + path
