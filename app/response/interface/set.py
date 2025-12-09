"""
Функции создания данных ответов
Возвращают результат в едином формате
"""
from ..models import Response
from app.config.models import Assistant, Satellite
from app.users.models import User


def save_response(parametrs: str, domen_url: str, html: str, user_id: int, model: str, assistant_key: str, source: str = "excel"):
    """
    Сохранение ответа от микросервиса
    
    Args:
        parametrs: JSON строка с входными параметрами
        domen_url: URL домена ("main" или URL сателлита)
        html: HTML результат
        user_id: ID пользователя
        model: название модели
        assistant_key: ключ ассистента (key_title)
        source: источник ("manual" или "excel")
    
    Returns:
        dict: {"success": bool, "data": dict, "error": str}
    """
    try:
        # Получаем login пользователя по user_id
        user_login = "excel_service"
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                user_login = user.login
            except User.DoesNotExist:
                pass
        
        # Получаем title ассистента по key_title
        try:
            assistant = Assistant.objects.get(key_title=assistant_key)
            assistant_title = assistant.title
        except Assistant.DoesNotExist:
            # Если не нашли — используем key_title как есть
            assistant_title = assistant_key
        
        # Получаем title домена по URL
        # Если "main" или пустой — сохраняем "main"
        # Если URL — ищем сателлит и берём title
        domen_title = "main"
        if domen_url and domen_url != "main":
            try:
                satellite = Satellite.objects.get(domen=domen_url)
                domen_title = satellite.title
            except Satellite.DoesNotExist:
                # Если не нашли — сохраняем URL как есть
                domen_title = domen_url
        
        response = Response.objects.create(
            parametrs=parametrs,
            domen=domen_title,
            html=html,
            user=user_login,
            model=model,
            assistant=assistant_title,
            source=source
        )
        
        return {
            "success": True,
            "data": {
                "id": response.id,
                "createAt": response.createAt.isoformat()
            },
            "error": None
        }
        
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": f"Ошибка при сохранении ответа: {str(e)}"
        }
