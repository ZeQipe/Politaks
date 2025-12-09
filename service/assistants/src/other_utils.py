import httpx
from .settings import logger

# URL Django сервера
DJANGO_API_URL = "http://localhost:8000/api/products"


async def get_related_products(domain: str, products_name: list[str]) -> dict:
    """Получение связанных товаров через Django API.

    Args:
        domain: домен ("main" или URL сателлита)
        products_name: список названий товаров

    Returns:
        dict: словарь связанных товаров {название: {link, description}}

    """
    try:
        params = {"product_name": products_name}
        if domain and domain != "main":
            params["domain_url"] = domain

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{DJANGO_API_URL}/links/", params=params)

        if response.status_code == 200:
            return response.json()
        else:
            logger.warning(f"get_related_products() failed: {response.status_code} - {response.text}")
            return {}

    except Exception as e:
        logger.error(f"get_related_products() error: {e}")
        return {}


async def get_products_links(domain: str, products_name: list[str]):
    """Получение ссылки на товар через Django API.

    Args:
        domain: домен ("main" или URL сателлита)
        products_name: список названий товаров или ["_all"] для всех
    Returns:
        str или dict: ссылка на товар или словарь всех ссылок

    """
    try:
        params = {"product_name": products_name}
        if domain and domain != "main":
            params["domain_url"] = domain

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{DJANGO_API_URL}/link/", params=params)

        if response.status_code == 200:
            return response.json()
        else:
            logger.warning(f"get_product_link() failed: {response.status_code} - {response.text}")
            return {}

    except Exception as e:
        logger.error(f"get_product_link() error: {e}")
        return {}
