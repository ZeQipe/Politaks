"""
Функции удаления данных для Settings API
Возвращают данные в формате OpenAPI спецификации
"""
from app.users.models import User
from app.config.models import Models
from app.product.models import Satellite, Products


def delete_goods(goods_id: int, user_id: int = None):
    """
    Удалить товар
    
    DELETE /settings/goods/{id}
    
    Args:
        goods_id: ID товара
        user_id: ID пользователя (для проверки владельца, опционально)
    
    Returns:
        dict: {"success": "true"}
    """
    try:
        # Находим товар
        try:
            product = Products.objects.get(id=goods_id)
        except Products.DoesNotExist:
            return {
                "success": "false",
                "error": f"Товар с ID '{goods_id}' не найден"
            }
        
        # Проверяем владельца (опционально)
        # if user_id and product.created_by_id != user_id:
        #     return {
        #         "success": "false",
        #         "error": "Нет прав на удаление этого товара"
        #     }
        
        # Удаляем товар
        product.delete()
        
        return {
            "success": "true"
        }
    except Exception as e:
        return {
            "success": "false",
            "error": f"Ошибка при удалении товара: {str(e)}"
        }


def delete_model(model_id: int):
    """
    Удалить AI модель
    
    DELETE /settings/models/{id}
    
    Args:
        model_id: ID модели
    
    Returns:
        dict: {"success": "true"}
    """
    try:
        # Находим модель
        try:
            model = Models.objects.get(id=model_id)
        except Models.DoesNotExist:
            return {
                "success": "false",
                "error": f"Модель с ID '{model_id}' не найдена"
            }
        
        # Удаляем модель
        model.delete()
        
        return {
            "success": "true"
        }
    except Exception as e:
        return {
            "success": "false",
            "error": f"Ошибка при удалении модели: {str(e)}"
        }


def delete_satellite(satellite_id: int):
    """
    Удалить домен-сателлит
    
    DELETE /settings/satellites/{id}
    
    Args:
        satellite_id: ID сателлита
    
    Returns:
        dict: {"success": "true"}
    """
    try:
        # Находим сателлит
        try:
            satellite = Satellite.objects.get(id=satellite_id)
        except Satellite.DoesNotExist:
            return {
                "success": "false",
                "error": f"Сателлит с ID '{satellite_id}' не найден"
            }
        
        # Удаляем сателлит
        satellite.delete()
        
        return {
            "success": "true"
        }
    except Exception as e:
        return {
            "success": "false",
            "error": f"Ошибка при удалении сателлита: {str(e)}"
        }


def delete_employee(employee_id: int):
    """
    Удалить сотрудника
    
    DELETE /settings/employees/{id}
    
    Args:
        employee_id: ID сотрудника
    
    Returns:
        dict: {"success": "true"}
    """
    try:
        # Находим сотрудника
        try:
            user = User.objects.get(id=employee_id)
        except User.DoesNotExist:
            return {
                "success": "false",
                "error": f"Сотрудник с ID '{employee_id}' не найден"
            }
        
        # Мягкое удаление (деактивация) вместо полного удаления
        user.is_active = False
        user.save()
        
        return {
            "success": "true"
        }
    except Exception as e:
        return {
            "success": "false",
            "error": f"Ошибка при удалении сотрудника: {str(e)}"
        }

