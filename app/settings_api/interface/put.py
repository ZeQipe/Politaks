"""
Функции обновления данных для Settings API
Возвращают данные в формате OpenAPI спецификации
"""
from app.users.models import User, UserAssistant
from app.config.models import Models, Assistant
from app.product.models import Satellite, Products


def update_user_profile(user_id: int, first_name: str = None, last_name: str = None, 
                        current_password: str = None, new_password: str = None, 
                        excel_base_url: str = None):
    """
    Обновить профиль пользователя
    
    PATCH /settings/user
    
    Args:
        user_id: ID пользователя
        first_name: Имя (опционально)
        last_name: Фамилия (опционально)
        current_password: Текущий пароль (если меняется пароль)
        new_password: Новый пароль (опционально)
        excel_base_url: Базовая ссылка на Excel (опционально)
    
    Returns:
        dict: {"success": true, "data": {...}}
    """
    try:
        user = User.objects.get(id=user_id)
        
        # Обновляем имя
        if first_name is not None:
            if len(first_name) < 2:
                return {
                    "success": False,
                    "error": "Имя должно содержать минимум 2 символа"
                }
            user.firstName = first_name
        
        # Обновляем фамилию
        if last_name is not None:
            if len(last_name) < 2:
                return {
                    "success": False,
                    "error": "Фамилия должна содержать минимум 2 символа"
                }
            user.lastName = last_name
        
        # Обновляем пароль
        if new_password is not None:
            # Проверяем текущий пароль
            if not current_password:
                return {
                    "success": False,
                    "error": "Для смены пароля требуется текущий пароль"
                }
            
            if not user.check_password(current_password):
                return {
                    "success": False,
                    "error": "Неверный текущий пароль"
                }
            
            # Валидация нового пароля
            if len(new_password) < 8:
                return {
                    "success": False,
                    "error": "Пароль должен содержать минимум 8 символов"
                }
            
            has_lower = any(c.islower() for c in new_password)
            has_upper = any(c.isupper() for c in new_password)
            has_digit = any(c.isdigit() for c in new_password)
            
            if not (has_lower and has_upper and has_digit):
                return {
                    "success": False,
                    "error": "Пароль должен содержать строчные и заглавные буквы, а также цифры"
                }
            
            user.set_password(new_password)
        
        # Обновляем Excel URL
        if excel_base_url is not None:
            user.default_excel_url = excel_base_url
        
        user.save()
        
        return {
            "success": True,
            "data": {
                "id": str(user.id),
                "firstName": user.firstName,
                "lastName": user.lastName,
                "excelBaseUrl": user.default_excel_url or ""
            }
        }
    except User.DoesNotExist:
        return {
            "success": False,
            "error": f"Пользователь с ID '{user_id}' не найден"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Ошибка при обновлении профиля: {str(e)}"
        }


def update_task_sheet_mappings(user_id: int, mappings: list):
    """
    Обновить маппинги задач на листы Excel
    
    PATCH /settings/task-sheet-mappings
    
    Args:
        user_id: ID пользователя
        mappings: Список маппингов [{"taskId": "1", "sheetId": 1}, ...]
    
    Returns:
        dict: {"success": true, "data": [...]}
    """
    try:
        user = User.objects.get(id=user_id)
        
        # Обновляем или создаём маппинги
        for mapping in mappings:
            task_id = mapping.get("taskId")
            sheet_id = mapping.get("sheetId")
            
            if task_id is None or sheet_id is None:
                continue
            
            try:
                assistant = Assistant.objects.get(id=int(task_id))
                
                # Обновляем или создаём UserAssistant
                user_assistant, created = UserAssistant.objects.update_or_create(
                    user=user,
                    assistant=assistant,
                    defaults={"sheets_id": int(sheet_id)}
                )
            except (Assistant.DoesNotExist, ValueError):
                continue
        
        # Получаем обновлённые данные
        assistants = Assistant.objects.all().order_by('id')
        user_mappings = {
            ua.assistant_id: ua.sheets_id
            for ua in UserAssistant.objects.filter(user=user)
        }
        
        data = []
        for assistant in assistants:
            sheets_id = user_mappings.get(assistant.id)
            if sheets_id is None:
                sheets_id = assistant.default_sheets_id or 0
            
            data.append({
                "taskId": str(assistant.id),
                "taskName": assistant.title,
                "sheetId": sheets_id
            })
        
        return {
            "success": True,
            "data": data
        }
    except User.DoesNotExist:
        return {
            "success": False,
            "error": f"Пользователь с ID '{user_id}' не найден"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Ошибка при обновлении маппингов: {str(e)}"
        }


def update_goods(goods_id: int, user_id: int, name: str, description: str, 
                 base_url: str, satellite_url: str, selected_domains: list):
    """
    Обновить товар
    
    PATCH /settings/goods/{id}
    
    Args:
        goods_id: ID товара
        user_id: ID пользователя (кто редактирует)
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
        
        # Находим товар
        try:
            product = Products.objects.get(id=goods_id)
        except Products.DoesNotExist:
            return {
                "success": "false",
                "error": f"Товар с ID '{goods_id}' не найден"
            }
        
        # Обновляем товар
        product.title = name
        product.description = description or ""
        product.baseLink = base_url or ""
        product.satelitLink = satellite_url or ""
        
        # Устанавливаем кто последний редактировал
        product.last_edit_user_id = user_id
        
        product.save()
        
        # Обновляем привязанные домены
        if selected_domains is not None:
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
            "error": f"Ошибка при обновлении товара: {str(e)}"
        }


def update_model(model_id: int, name: str, key: str, url: str):
    """
    Обновить AI модель
    
    PATCH /settings/models/{id}
    
    Args:
        model_id: ID модели
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
        
        # Находим модель
        try:
            model = Models.objects.get(id=model_id)
        except Models.DoesNotExist:
            return {
                "success": "false",
                "error": f"Модель с ID '{model_id}' не найдена"
            }
        
        # Обновляем модель
        model.name = name
        model.url = url
        model.set_key(key)  # Перешифровываем ключ
        model.save()
        
        return {
            "success": "true",
            "data": {
                "id": str(model.id),
                "name": model.name,
                "key": model.get_key(),
                "url": model.url
            }
        }
    except Exception as e:
        return {
            "success": "false",
            "error": f"Ошибка при обновлении модели: {str(e)}"
        }


def update_satellite(satellite_id: int, name: str, domain: str):
    """
    Обновить домен-сателлит
    
    PATCH /settings/satellites/{id}
    
    Args:
        satellite_id: ID сателлита
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
        
        # Находим сателлит
        try:
            satellite = Satellite.objects.get(id=satellite_id)
        except Satellite.DoesNotExist:
            return {
                "success": "false",
                "error": f"Сателлит с ID '{satellite_id}' не найден"
            }
        
        # Проверяем уникальность домена (кроме текущего)
        if Satellite.objects.filter(domen=domain).exclude(id=satellite_id).exists():
            return {
                "success": "false",
                "error": f"Домен '{domain}' уже существует"
            }
        
        # Обновляем сателлит
        satellite.title = name
        satellite.domen = domain
        satellite.save()
        
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
            "error": f"Ошибка при обновлении сателлита: {str(e)}"
        }


def update_employee(employee_id: int, first_name: str, last_name: str, role: str,
                    new_password: str = None, confirm_password: str = None):
    """
    Обновить сотрудника
    
    PATCH /settings/employees/{id}
    
    Args:
        employee_id: ID сотрудника
        first_name: Имя
        last_name: Фамилия
        role: Роль
        new_password: Новый пароль (опционально)
        confirm_password: Подтверждение пароля (опционально)
    
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
        
        # Валидация роли
        valid_roles = [choice[0] for choice in User.ROLE_CHOICES]
        if role not in valid_roles:
            return {
                "success": "false",
                "error": f"Недопустимая роль. Допустимые: {', '.join(valid_roles)}"
            }
        
        # Находим сотрудника
        try:
            user = User.objects.get(id=employee_id)
        except User.DoesNotExist:
            return {
                "success": "false",
                "error": f"Сотрудник с ID '{employee_id}' не найден"
            }
        
        # Обновляем данные
        user.firstName = first_name
        user.lastName = last_name
        user.role = role
        
        # Обновляем пароль если указан
        if new_password:
            if new_password != confirm_password:
                return {
                    "success": "false",
                    "error": "Пароли не совпадают"
                }
            
            if len(new_password) < 8:
                return {
                    "success": "false",
                    "error": "Пароль должен содержать минимум 8 символов"
                }
            
            has_lower = any(c.islower() for c in new_password)
            has_upper = any(c.isupper() for c in new_password)
            has_digit = any(c.isdigit() for c in new_password)
            
            if not (has_lower and has_upper and has_digit):
                return {
                    "success": "false",
                    "error": "Пароль должен содержать строчные и заглавные буквы, а также цифры"
                }
            
            user.set_password(new_password)
        
        user.save()
        
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
            "error": f"Ошибка при обновлении сотрудника: {str(e)}"
        }

