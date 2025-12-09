"""
Интерфейс для работы с сервисом Assistants (порт 8001)
"""
import os
import httpx
from typing import Optional


class AssistantsAPI:
    """Клиент для API сервиса Assistants"""
    
    def __init__(self, base_url: str = None, timeout: float = 120.0):
        self.base_url = base_url or os.getenv('ASSISTANTS_API_URL', 'http://localhost:8001')
        self.timeout = timeout
    
    async def _post(self, endpoint: str, payload: dict) -> dict:
        """Базовый POST запрос"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(f"{self.base_url}{endpoint}", json=payload)
            response.raise_for_status()
            return response.json()
    
    async def _post_multipart(self, endpoint: str, data: dict, files: dict = None) -> dict:
        """POST запрос с multipart/form-data"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(f"{self.base_url}{endpoint}", data=data, files=files)
            response.raise_for_status()
            return response.json()

    # =========================================================================
    # /api/v1/change/...
    # =========================================================================

    async def change_subdescription(
        self,
        llm_model: str,
        domain: str,
        product_name: str,
        description: str,
        usage: str,
        seo_high_freq: str = "",
        seo_medium_freq: str = "",
        seo_low_freq: str = "",
    ) -> str:
        """
        Краткое SEO-описание товара (~3000 символов)
        
        Returns:
            sub_description: HTML строка
        """
        payload = {
            "llm_model": llm_model,
            "domain": domain,
            "product_name": product_name,
            "description": description,
            "usage": usage,
            "seo_high_freq": seo_high_freq,
            "seo_medium_freq": seo_medium_freq,
            "seo_low_freq": seo_low_freq,
        }
        result = await self._post("/api/v1/change/subdescription", payload)
        return result["sub_description"]

    async def change_description(
        self,
        llm_model: str,
        domain: str,
        product_name: str,
        description: str,
        usage: Optional[str] = None,
        seo_high_freq: str = "",
        seo_medium_freq: str = "",
        seo_low_freq: str = "",
    ) -> str:
        """
        Полное HTML-описание товара
        
        Returns:
            description: HTML строка
        """
        payload = {
            "llm_model": llm_model,
            "domain": domain,
            "product_name": product_name,
            "description": description,
            "usage": usage,
            "seo_high_freq": seo_high_freq,
            "seo_medium_freq": seo_medium_freq,
            "seo_low_freq": seo_low_freq,
        }
        result = await self._post("/api/v1/change/description", payload)
        return result["description"]

    async def change_usage(
        self,
        llm_model: str,
        usage: str,
        domain: Optional[str] = None,
        product_name: Optional[str] = None,
    ) -> str:
        """
        Форматирование текста применения в HTML
        
        Returns:
            usage: HTML строка
        """
        payload = {
            "llm_model": llm_model,
            "domain": domain,
            "product_name": product_name,
            "usage": usage,
        }
        result = await self._post("/api/v1/change/usage", payload)
        return result["usage"]

    async def change_features(
        self,
        llm_model: str,
        features: str,
        domain: Optional[str] = None,
        product_name: Optional[str] = None,
    ) -> str:
        """
        Форматирование свойств товара в HTML-таблицу
        
        Returns:
            features: HTML таблица
        """
        payload = {
            "llm_model": llm_model,
            "domain": domain,
            "product_name": product_name,
            "features": features,
        }
        result = await self._post("/api/v1/change/features", payload)
        return result["features"]

    async def change_article(
        self,
        llm_model: str,
        title: str,
        article: str,
        seo_high_freq: str = "",
        seo_medium_freq: str = "",
        seo_low_freq: str = "",
    ) -> str:
        """
        Перефразирование статьи (рерайт)
        
        Returns:
            article: HTML строка
        """
        payload = {
            "llm_model": llm_model,
            "title": title,
            "article": article,
            "seo_high_freq": seo_high_freq,
            "seo_medium_freq": seo_medium_freq,
            "seo_low_freq": seo_low_freq,
        }
        result = await self._post("/api/v1/change/article", payload)
        return result["article"]

    async def change_tech_instruction(
        self,
        llm_model: str,
        domain: str,
        tech_instruction: str,
        seo_high_freq: str = "",
        seo_medium_freq: str = "",
        seo_low_freq: str = "",
    ) -> str:
        """
        Рерайт технической инструкции
        
        Returns:
            tech_instruction: HTML строка
        """
        payload = {
            "llm_model": llm_model,
            "domain": domain,
            "tech_instruction": tech_instruction,
            "seo_high_freq": seo_high_freq,
            "seo_medium_freq": seo_medium_freq,
            "seo_low_freq": seo_low_freq,
        }
        result = await self._post("/api/v1/change/tech_instruction", payload)
        return result["tech_instruction"]

    async def change_category_description(
        self,
        llm_model: str,
        domain: str,
        category_description: str,
        seo_high_freq: str = "",
        seo_medium_freq: str = "",
        seo_low_freq: str = "",
    ) -> str:
        """
        Рерайт описания категории
        
        Returns:
            category_description: HTML строка
        """
        payload = {
            "llm_model": llm_model,
            "domain": domain,
            "category_description": category_description,
            "seo_high_freq": seo_high_freq,
            "seo_medium_freq": seo_medium_freq,
            "seo_low_freq": seo_low_freq,
        }
        result = await self._post("/api/v1/change/category_description", payload)
        return result["category_description"]

    # =========================================================================
    # /api/v1/create/...
    # =========================================================================

    async def create_preview(
        self,
        llm_model: str,
        domain: str,
        product_name: str,
        description: str,
        usage: Optional[str] = None,
        seo_high_freq: str = "",
        seo_medium_freq: str = "",
        seo_low_freq: str = "",
    ) -> str:
        """
        Превью товара (2-3 предложения)
        
        Returns:
            preview: текстовая строка
        """
        payload = {
            "llm_model": llm_model,
            "domain": domain,
            "product_name": product_name,
            "description": description,
            "usage": usage,
            "seo_high_freq": seo_high_freq,
            "seo_medium_freq": seo_medium_freq,
            "seo_low_freq": seo_low_freq,
        }
        result = await self._post("/api/v1/create/previews", payload)
        return result["preview"]

    async def create_reviews(
        self,
        llm_model: str,
        product_name: str,
        description: str,
        usage: Optional[str] = None,
        seo_high_freq: str = "",
        seo_medium_freq: str = "",
        seo_low_freq: str = "",
    ) -> list[dict]:
        """
        Генерация 3 отзывов на товар
        
        Returns:
            reviews: список из 3 отзывов
            [
                {
                    "author": str,
                    "rating": int (1-5),
                    "experience_of_use": str,
                    "pros": str,
                    "cons": str,
                    "review": str
                },
                ...
            ]
        """
        payload = {
            "llm_model": llm_model,
            "product_name": product_name,
            "description": description,
            "usage": usage,
            "seo_high_freq": seo_high_freq,
            "seo_medium_freq": seo_medium_freq,
            "seo_low_freq": seo_low_freq,
        }
        result = await self._post("/api/v1/create/reviews", payload)
        return result["reviews"]

    async def create_work_results(
        self,
        llm_model: str,
        domain: str,
        place_name: str,
        location: str,
        background_info: str,
        products_name: str,
        descriptions: str,
        photo1: Optional[bytes] = None,
        photo2: Optional[bytes] = None,
    ) -> str:
        """
        Описание выполненных работ (с фото)
        
        Returns:
            work_results: HTML строка
        """
        data = {
            "llm_model": llm_model,
            "domain": domain,
            "place_name": place_name,
            "location": location,
            "background_info": background_info,
            "products_name": products_name,
            "descriptions": descriptions,
        }
        files = {}
        if photo1:
            files["photo1"] = ("photo1.jpg", photo1, "image/jpeg")
        if photo2:
            files["photo2"] = ("photo2.jpg", photo2, "image/jpeg")
        
        result = await self._post_multipart("/api/v1/create/work_results", data, files or None)
        return result["work_results"]

    async def create_article(
        self,
        llm_model: str,
        topic: str,
        comment: str,
        seo_high_freq: str = "",
        seo_medium_freq: str = "",
        seo_low_freq: str = "",
    ) -> str:
        """
        Создание новой статьи
        
        Returns:
            article: HTML строка
        """
        payload = {
            "llm_model": llm_model,
            "topic": topic,
            "comment": comment,
            "seo_high_freq": seo_high_freq,
            "seo_medium_freq": seo_medium_freq,
            "seo_low_freq": seo_low_freq,
        }
        result = await self._post("/api/v1/create/article", payload)
        return result["article"]

