"""
Функции создания данных конфигурации
Возвращают результат в едином формате
"""
import json
import asyncio
from ..models import Models, Assistant
from app.product.models import Satellite
from app.response.models import Response
from interface import AssistantsAPI


# Маппинг key_title → метод AssistantsAPI
ASSISTANT_METHODS = {
    "sub_description": "change_subdescription",
    "description": "change_description",
    "usage": "change_usage",
    "features": "change_features",
    "preview": "create_preview",
    "reviews": "create_reviews",
    "work_results": "create_work_results",
    "change_article": "change_article",
    "article": "create_article",
    "tech_instruction": "change_tech_instruction",
    "category_description": "change_category_description",
}


def generate_content(task_id: str, model_id: str, domain_id: str, fields: list, user: str = "anonymous", files: dict = None):
    """
    Генерация контента
    
    Args:
        task_id: ID ассистента (строка)
        model_id: ID модели (строка)
        domain_id: ID домена ('main' или ID Satellite)
        fields: массив полей [{name: str, value: str}]
        user: имя пользователя
        files: словарь файлов {name: bytes} для work_results
    
    Returns:
        dict: {"success": bool, "data": dict, "error": str}
    """
    try:
        # Валидация ассистента по ID
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
        
        # Проверяем, есть ли метод для этого ассистента
        method_name = ASSISTANT_METHODS.get(assistant.key_title)
        if not method_name:
            return {
                "success": False,
                "data": None,
                "error": f"Неизвестный тип ассистента: '{assistant.key_title}'"
            }
        
        # Преобразуем fields в словарь {name: value}
        fields_dict = {field.get('name'): field.get('value') for field in fields}
        
        # Формируем payload для API
        payload = _build_payload(
            assistant_key=assistant.key_title,
            llm_model=model.name,
            domain=domain_value,
            fields_dict=fields_dict,
            files=files
        )
        
        if payload is None:
            return {
                "success": False,
                "data": None,
                "error": f"Не удалось сформировать payload для ассистента '{assistant.key_title}'"
            }
        
        # Вызываем API ассистента
        print(f"=== PAYLOAD для {assistant.key_title} ===")
        print(json.dumps(payload, indent=2, ensure_ascii=False, default=str))
        print("=" * 50)
        
        api = AssistantsAPI()
        method = getattr(api, method_name)
        
        # Запускаем async метод в sync контексте
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(method(**payload))
        finally:
            loop.close()
        
        # Обрабатываем результат
        generated_html = _format_result(assistant.key_title, result)
        generated_text = _strip_html(generated_html)
        
        # Формируем параметры для сохранения
        params = json.dumps(fields, ensure_ascii=False)
        
        # Сохраняем в Response
        Response.objects.create(
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


def _build_payload(assistant_key: str, llm_model: str, domain: str, fields_dict: dict, files: dict = None) -> dict:
    """
    Формирует payload для конкретного ассистента
    
    Args:
        assistant_key: ключ ассистента (key_title)
        llm_model: название модели
        domain: домен (main или URL сателлита)
        fields_dict: словарь {name: value}
        files: словарь файлов {name: bytes}
    
    Returns:
        dict: payload для API или None если ошибка
    """
    
    # Базовые поля, которые есть у большинства ассистентов
    base_payload = {"llm_model": llm_model}
    
    if assistant_key == "sub_description":
        # change_subdescription(llm_model, domain, product_name, description, usage, seo_*)
        return {
            **base_payload,
            "domain": domain,
            "product_name": fields_dict.get("product_name", ""),
            "description": fields_dict.get("description", ""),
            "usage": fields_dict.get("usage", ""),
            "seo_high_freq": fields_dict.get("seo_high_freq", ""),
            "seo_medium_freq": fields_dict.get("seo_medium_freq", ""),
            "seo_low_freq": fields_dict.get("seo_low_freq", ""),
        }
    
    elif assistant_key == "description":
        # change_description(llm_model, domain, product_name, description, usage?, seo_*)
        return {
            **base_payload,
            "domain": domain,
            "product_name": fields_dict.get("product_name", ""),
            "description": fields_dict.get("description", ""),
            "usage": fields_dict.get("usage"),
            "seo_high_freq": fields_dict.get("seo_high_freq", ""),
            "seo_medium_freq": fields_dict.get("seo_medium_freq", ""),
            "seo_low_freq": fields_dict.get("seo_low_freq", ""),
        }
    
    elif assistant_key == "usage":
        # change_usage(llm_model, usage, domain?, product_name?)
        return {
            **base_payload,
            "usage": fields_dict.get("usage", ""),
            "domain": domain if domain != "main" else None,
            "product_name": fields_dict.get("product_name"),
        }
    
    elif assistant_key == "features":
        # change_features(llm_model, features, domain?, product_name?)
        return {
            **base_payload,
            "features": fields_dict.get("features", ""),
            "domain": domain if domain != "main" else None,
            "product_name": fields_dict.get("product_name"),
        }
    
    elif assistant_key == "preview":
        # create_preview(llm_model, domain, product_name, description, usage?, seo_*)
        return {
            **base_payload,
            "domain": domain,
            "product_name": fields_dict.get("product_name", ""),
            "description": fields_dict.get("description", ""),
            "usage": fields_dict.get("usage"),
            "seo_high_freq": fields_dict.get("seo_high_freq", ""),
            "seo_medium_freq": fields_dict.get("seo_medium_freq", ""),
            "seo_low_freq": fields_dict.get("seo_low_freq", ""),
        }
    
    elif assistant_key == "reviews":
        # create_reviews(llm_model, product_name, description, usage?, seo_*)
        return {
            **base_payload,
            "product_name": fields_dict.get("product_name", ""),
            "description": fields_dict.get("description", ""),
            "usage": fields_dict.get("usage"),
            "seo_high_freq": fields_dict.get("seo_high_freq", ""),
            "seo_medium_freq": fields_dict.get("seo_medium_freq", ""),
            "seo_low_freq": fields_dict.get("seo_low_freq", ""),
        }
    
    elif assistant_key == "work_results":
        # create_work_results(llm_model, domain, place_name, location, background_info, products_name, descriptions, photo1?, photo2?)
        # products_name может быть массивом (multiple select) — преобразуем в строку через запятую
        products_name = fields_dict.get("products_name", "")
        if isinstance(products_name, list):
            products_name = ", ".join(products_name)
        
        payload = {
            **base_payload,
            "domain": domain,
            "place_name": fields_dict.get("place_name", ""),
            "location": fields_dict.get("location", ""),
            "background_info": fields_dict.get("background_info", ""),
            "products_name": products_name,
            "descriptions": fields_dict.get("descriptions", ""),
        }
        # Добавляем файлы если есть
        if files:
            payload["photo1"] = files.get("photo1")
            payload["photo2"] = files.get("photo2")
        return payload
    
    elif assistant_key == "change_article":
        # change_article(llm_model, title, article, seo_*)
        return {
            **base_payload,
            "title": fields_dict.get("title", ""),
            "article": fields_dict.get("article", ""),
            "seo_high_freq": fields_dict.get("seo_high_freq", ""),
            "seo_medium_freq": fields_dict.get("seo_medium_freq", ""),
            "seo_low_freq": fields_dict.get("seo_low_freq", ""),
        }
    
    elif assistant_key == "article":
        # create_article(llm_model, topic, comment, seo_*)
        return {
            **base_payload,
            "topic": fields_dict.get("topic", ""),
            "comment": fields_dict.get("comment", ""),
            "seo_high_freq": fields_dict.get("seo_high_freq", ""),
            "seo_medium_freq": fields_dict.get("seo_medium_freq", ""),
            "seo_low_freq": fields_dict.get("seo_low_freq", ""),
        }
    
    elif assistant_key == "tech_instruction":
        # change_tech_instruction(llm_model, domain, tech_instruction, seo_*)
        return {
            **base_payload,
            "domain": domain,
            "tech_instruction": fields_dict.get("tech_instruction", ""),
            "seo_high_freq": fields_dict.get("seo_high_freq", ""),
            "seo_medium_freq": fields_dict.get("seo_medium_freq", ""),
            "seo_low_freq": fields_dict.get("seo_low_freq", ""),
        }
    
    elif assistant_key == "category_description":
        # change_category_description(llm_model, domain, category_description, seo_*)
        return {
            **base_payload,
            "domain": domain,
            "category_description": fields_dict.get("category_description", ""),
            "seo_high_freq": fields_dict.get("seo_high_freq", ""),
            "seo_medium_freq": fields_dict.get("seo_medium_freq", ""),
            "seo_low_freq": fields_dict.get("seo_low_freq", ""),
        }
    
    return None


def _format_result(assistant_key: str, result) -> str:
    """
    Форматирует результат в HTML
    
    Args:
        assistant_key: ключ ассистента
        result: результат от API (строка или список для reviews)
    
    Returns:
        str: HTML строка
    """
    if assistant_key == "reviews":
        # Для отзывов возвращается список
        if isinstance(result, list):
            reviews_html = "<div class='reviews'>"
            for review in result:
                reviews_html += f"""
                <div class='review'>
                    <div class='review-header'>
                        <span class='author'>{review.get('author', '')}</span>
                        <span class='rating'>{'★' * review.get('rating', 5)}</span>
                    </div>
                    <div class='experience'>Опыт использования: {review.get('experience_of_use', '')}</div>
                    <div class='pros'><strong>Плюсы:</strong> {review.get('pros', '')}</div>
                    <div class='cons'><strong>Минусы:</strong> {review.get('cons', '')}</div>
                    <div class='text'>{review.get('review', '')}</div>
                </div>
                """
            reviews_html += "</div>"
            return reviews_html
        return str(result)
    
    # Для остальных ассистентов результат - строка HTML
    return str(result) if result else ""


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
