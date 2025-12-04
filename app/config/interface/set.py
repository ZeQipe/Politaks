"""
Функции создания данных конфигурации
Возвращают результат в едином формате
"""
import json
from ..models import Models, Assistant
from app.product.models import Satellite
from app.response.models import Response


def generate_content(task_id: str, model_id: str, domain_id: str, fields: list, user: str = "anonymous"):
    """
    Генерация контента
    
    Args:
        task_id: ID ассистента
        model_id: ID модели
        domain_id: ID домена ('main' или ID Satellite)
        fields: массив полей [{name: str, value: str}]
        user: имя пользователя
    
    Returns:
        dict: {"success": bool, "data": dict, "error": str}
    """
    try:
        # Валидация ассистента
        try:
            assistant = Assistant.objects.get(id=task_id)
        except Assistant.DoesNotExist:
            return {
                "success": False,
                "data": None,
                "error": f"Ассистент с ID '{task_id}' не найден"
            }
        
        # Валидация модели
        try:
            model = Models.objects.get(id=model_id)
        except Models.DoesNotExist:
            return {
                "success": False,
                "data": None,
                "error": f"Модель с ID '{model_id}' не найдена"
            }
        
        # Определяем домен
        if domain_id == 'main':
            domain_value = "main"
        else:
            try:
                satellite = Satellite.objects.get(id=domain_id)
                domain_value = satellite.domen
            except Satellite.DoesNotExist:
                return {
                    "success": False,
                    "data": None,
                    "error": f"Домен с ID '{domain_id}' не найден"
                }
        
        # Формируем параметры для сохранения
        params = json.dumps(fields, ensure_ascii=False)
        
        # TODO: Здесь будет интеграция с AI
        # Пока возвращаем заглушку
        generated_html = _generate_mock_response(assistant, model, fields)
        generated_text = _strip_html(generated_html)
        
        # Сохраняем в Response
        response = Response.objects.create(
            parametrs=params,
            domen=domain_value,
            html=generated_html,
            user=user,
            model=model.name,
            assistant=assistant.title,
            source='manual'
        )
        
        return {
            "success": True,
            "data": {
                "html": generated_html,
                "text": generated_text
            },
            "error": None
        }
        
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": f"Ошибка при генерации: {str(e)}"
        }


def _generate_mock_response(assistant, model, fields):
    """
    Заглушка для генерации контента
    TODO: Заменить на реальную интеграцию с AI
    """
    fields_html = ""
    for field in fields:
        fields_html += f"<p><strong>{field.get('name', 'field')}:</strong> {field.get('value', '')}</p>\n"
    
    return f"""
<div class="generated-content">
    <h2>Сгенерированный контент</h2>
    <p><em>Ассистент: {assistant.title}</em></p>
    <p><em>Модель: {model.name}</em></p>
    <hr>
    <h3>Входные данные:</h3>
    {fields_html}
    <hr>
    <p><strong>TODO:</strong> Здесь будет реальный ответ от AI</p>
</div>
"""


def _strip_html(html: str) -> str:
    """
    Удаление HTML тегов для получения текста
    """
    import re
    clean = re.compile('<.*?>')
    text = re.sub(clean, '', html)
    # Убираем лишние пробелы и переносы
    text = ' '.join(text.split())
    return text
