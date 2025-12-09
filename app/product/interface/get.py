"""
Функции получения данных товаров
Возвращают данные в едином формате
"""
from ..models import Products, Satellite, List


def get_related_products_by_domain(product_names: list, domain_url: str = None):
    """
    Получение связанных товаров с учетом домена
    
    Args:
        product_names: Список названий товаров
        domain_url: title или URL домена (None/"main" = базовые ссылки)
    
    Returns:
        dict: {
            "success": bool,
            "data": dict {название: {связанный_товар: {link, description}}},
            "error": str или None
        }
    """
    try:
        result = {}
        
        # Определяем сателлит если указан домен (и это не "main")
        satellite = None
        if domain_url and domain_url != "main":
            # Сначала ищем по title
            satellite = Satellite.objects.filter(title=domain_url).first()
            if not satellite:
                # Ищем по URL (пробуем оба варианта: со слешем и без)
                domain_with_slash = domain_url.rstrip('/') + '/'
                domain_without_slash = domain_url.rstrip('/')
                satellite = Satellite.objects.filter(domen__in=[domain_with_slash, domain_without_slash]).first()
            
            if not satellite:
                return {
                    "success": False,
                    "data": None,
                    "error": f"Домен '{domain_url}' не найден"
                }
        
        # Обрабатываем каждый товар
        for product_name in product_names:
            try:
                product = Products.objects.get(title=product_name)
            except Products.DoesNotExist:
                result[product_name] = {}
                continue
            
            # Получаем все связи текущего товара
            relations = List.objects.filter(product=product).select_related('related_product')
            
            # Фильтруем связанные товары
            product_relations = {}
            
            for relation in relations:
                related_product = relation.related_product
                
                # Фильтрация в зависимости от наличия домена
                if domain_url is None or domain_url == "main":
                    # Если домен None или "main" - нужны товары с baseLink
                    if not related_product.baseLink:
                        continue
                    link = related_product.baseLink
                else:
                    # Если домен есть - проверяем, есть ли у связанного товара этот сателлит
                    if satellite not in related_product.satelitDomens.all():
                        continue
                    # Проверяем наличие satelitLink
                    if not related_product.satelitLink:
                        continue
                    # Склеиваем домен + satelitLink
                    link = _join_url(satellite.domen, related_product.satelitLink)
                
                # Формируем результат
                product_relations[related_product.title] = {
                    "link": link,
                    "description": relation.description or ""
                }
            
            result[product_name] = product_relations
        
        return {
            "success": True,
            "data": result,
            "error": None
        }
        
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": f"Ошибка при получении данных: {str(e)}"
        }


def get_product_link_by_domain(product_names: list, domain_url: str = None):
    """
    Получение ссылок на товары с учетом домена
    
    Args:
        product_names: Список названий товаров или ["_all"] для всех
        domain_url: title или URL домена (None/"main" = базовые ссылки)
    
    Returns:
        dict: {
            "success": bool,
            "data": dict {название: ссылка},
            "error": str или None
        }
    """
    try:
        result = {}
        
        # Определяем сателлит если указан домен
        satellite = None
        if domain_url and domain_url != "main":
            # Сначала ищем по title
            satellite = Satellite.objects.filter(title=domain_url).first()
            if not satellite:
                # Ищем по URL (пробуем оба варианта: со слешем и без)
                domain_with_slash = domain_url.rstrip('/') + '/'
                domain_without_slash = domain_url.rstrip('/')
                satellite = Satellite.objects.filter(domen__in=[domain_with_slash, domain_without_slash]).first()
            
            if not satellite:
                return {
                    "success": False,
                    "data": None,
                    "error": f"Домен '{domain_url}' не найден"
                }
        
        # Специальный случай: запрос всех товаров
        if product_names == ["_all"]:
            if domain_url is None or domain_url == "main":
                # Базовые ссылки - все товары с baseLink
                products = Products.objects.filter(baseLink__isnull=False).exclude(baseLink='')
                for product in products:
                    result[product.title] = product.baseLink
            else:
                # Товары этого сателлита с satelitLink
                products = satellite.products.filter(satelitLink__isnull=False).exclude(satelitLink='')
                for product in products:
                    result[product.title] = _join_url(satellite.domen, product.satelitLink)
            
            return {
                "success": True,
                "data": result,
                "error": None
            }
        
        # Обрабатываем каждый товар
        for product_name in product_names:
            try:
                product = Products.objects.get(title=product_name)
            except Products.DoesNotExist:
                result[product_name] = ""
                continue
            
            # Определяем ссылку в зависимости от домена
            if domain_url is None or domain_url == "main":
                # Базовая ссылка
                result[product_name] = product.baseLink or ""
            else:
                # Проверяем, есть ли товар на этом сателлите
                if satellite not in product.satelitDomens.all():
                    result[product_name] = ""
                    continue
                
                # Склеиваем домен + satelitLink
                if product.satelitLink:
                    result[product_name] = _join_url(satellite.domen, product.satelitLink)
                else:
                    result[product_name] = ""
        
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
