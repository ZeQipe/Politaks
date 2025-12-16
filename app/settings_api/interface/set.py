"""
Функции создания данных для Settings API
Возвращают данные в формате OpenAPI спецификации
"""
from app.users.models import User
from app.config.models import Models
from app.product.models import Satellite, Products


def create_goods(user_id: int, name: str, description: str, base_url: str, satellite_url: str, selected_domains: list):
    """
    Создать товар
    
    POST /settings/goods
    
    Args:
        user_id: ID пользователя (создателя)
        name: Название товара
        description: Описание товара
        base_url: Базовый URL
        satellite_url: URL сателлита
        selected_domains: Список доменов [{"id": "1", "name": "...", "domain": "..."}]
    
    Returns:
        dict: {"success": "true", "data": {...}}
    """
    try:
        # Валидация
        if not name or len(name) < 2:
            return {
                "success": "false",
                "error": "Название товара должно содержать минимум 2 символа"
            }
        
        # Получаем пользователя
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return {
                "success": "false",
                "error": f"Пользователь с ID '{user_id}' не найден"
            }
        
        # Создаём товар
        product = Products.objects.create(
            title=name,
            description=description or "",
            baseLink=base_url or "",
            satelitLink=satellite_url or "",
            created_by=user
        )
        
        # Привязываем домены
        if selected_domains:
            domain_ids = [int(d.get("id")) for d in selected_domains if d.get("id")]
            satellites = Satellite.objects.filter(id__in=domain_ids)
            product.satelitDomens.set(satellites)
        
        # Формируем ответ
        selected_domains_response = []
        for satellite in product.satelitDomens.all():
            selected_domains_response.append({
                "id": str(satellite.id),
                "name": satellite.title,
                "domain": satellite.domen
            })
        
        return {
            "success": "true",
            "data": {
                "id": str(product.id),
                "name": product.title,
                "description": product.description or "",
                "baseUrl": product.baseLink or "",
                "satelliteUrl": product.satelitLink or "",
                "selectedDomain": selected_domains_response
            }
        }
    except Exception as e:
        return {
            "success": "false",
            "error": f"Ошибка при создании товара: {str(e)}"
        }


def create_model(name: str, key: str, url: str):
    """
    Создать AI модель
    
    POST /settings/models
    
    Args:
        name: Наименование модели
        key: API ключ
        url: URL API модели
    
    Returns:
        dict: {"success": "true", "data": {...}}
    """
    try:
        # Валидация
        if not name or len(name) < 2:
            return {
                "success": "false",
                "error": "Название модели должно содержать минимум 2 символа"
            }
        
        if not key or len(key) < 2:
            return {
                "success": "false",
                "error": "Ключ модели должен содержать минимум 2 символа"
            }
        
        if not url:
            return {
                "success": "false",
                "error": "URL модели обязателен"
            }
        
        # Создаём модель
        model = Models(
            name=name,
            url=url
        )
        model.set_key(key)  # Шифруем ключ
        model.save()
        
        return {
            "success": "true",
            "data": {
                "id": str(model.id),
                "name": model.name,
                "key": model.get_key(),  # Расшифровываем для ответа
                "url": model.url
            }
        }
    except Exception as e:
        return {
            "success": "false",
            "error": f"Ошибка при создании модели: {str(e)}"
        }


def create_satellite(name: str, domain: str):
    """
    Создать домен-сателлит
    
    POST /settings/satellites
    
    Args:
        name: Наименование домена
        domain: Домен
    
    Returns:
        dict: {"success": "true", "data": {...}}
    """
    try:
        # Валидация
        if not name or len(name) < 2:
            return {
                "success": "false",
                "error": "Наименование домена должно содержать минимум 2 символа"
            }
        
        if not domain:
            return {
                "success": "false",
                "error": "Домен обязателен"
            }
        
        # Проверка уникальности домена
        if Satellite.objects.filter(domen=domain).exists():
            return {
                "success": "false",
                "error": f"Домен '{domain}' уже существует"
            }
        
        # Создаём сателлит
        satellite = Satellite.objects.create(
            title=name,
            domen=domain
        )
        
        return {
            "success": "true",
            "data": {
                "id": str(satellite.id),
                "name": satellite.title,
                "domain": satellite.domen
            }
        }
    except Exception as e:
        return {
            "success": "false",
            "error": f"Ошибка при создании сателлита: {str(e)}"
        }


def create_employee(first_name: str, last_name: str, role: str, password: str):
    """
    Создать сотрудника
    
    POST /settings/employees
    
    Args:
        first_name: Имя
        last_name: Фамилия
        role: Роль (admin, moderator, user)
        password: Пароль
    
    Returns:
        dict: {"success": "true", "data": {...}}
    """
    try:
        # Валидация
        if not first_name or len(first_name) < 2:
            return {
                "success": "false",
                "error": "Имя должно содержать минимум 2 символа"
            }
        
        if not last_name or len(last_name) < 2:
            return {
                "success": "false",
                "error": "Фамилия должна содержать минимум 2 символа"
            }
        
        if not password or len(password) < 8:
            return {
                "success": "false",
                "error": "Пароль должен содержать минимум 8 символов"
            }
        
        # Валидация пароля: буквы и цифры
        has_lower = any(c.islower() for c in password)
        has_upper = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        
        if not (has_lower and has_upper and has_digit):
            return {
                "success": "false",
                "error": "Пароль должен содержать строчные и заглавные буквы, а также цифры"
            }
        
        # Валидация роли
        valid_roles = [choice[0] for choice in User.ROLE_CHOICES]
        if role not in valid_roles:
            return {
                "success": "false",
                "error": f"Недопустимая роль. Допустимые: {', '.join(valid_roles)}"
            }
        
        # Генерируем уникальный логин
        base_login = f"{first_name.lower()}_{last_name.lower()}"
        login = base_login
        counter = 1
        while User.objects.filter(login=login).exists():
            login = f"{base_login}_{counter}"
            counter += 1
        
        # Создаём пользователя
        user = User.objects.create_user(
            login=login,
            password=password,
            firstName=first_name,
            lastName=last_name,
            role=role
        )
        
        return {
            "success": "true",
            "data": {
                "id": str(user.id),
                "firstName": user.firstName,
                "lastName": user.lastName,
                "role": user.role
            }
        }
    except Exception as e:
        return {
            "success": "false",
            "error": f"Ошибка при создании сотрудника: {str(e)}"
        }

