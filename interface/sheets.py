"""
Интерфейс для работы с сервисом Sheets (порт 8002)
"""
import os
import httpx
from typing import Optional


class SheetsAPI:
    """Клиент для API сервиса Sheets"""
    
    def __init__(self, base_url: str = None, timeout: float = 600.0):
        self.base_url = base_url or os.getenv('SHEETS_API_URL', 'http://localhost:7998')
        self.timeout = timeout  # Большой таймаут для обработки таблиц
    
    async def _post(self, endpoint: str, payload: dict) -> dict:
        """Базовый POST запрос"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(f"{self.base_url}{endpoint}", json=payload)
            response.raise_for_status()
            return response.json()

    async def process_sheet(
        self,
        llm_model: str,
        link: str,
        assistant: str,
        sheet_id: int = 0,
        from_row: int = 3,
        to_row: int = -1,
    ) -> dict:
        """
        Обработка одного листа Google таблицы
        
        Args:
            llm_model: Модель OpenAI (например "gpt-4.1")
            link: URL Google таблицы
            assistant: Тип ассистента:
                - sub_description
                - description
                - usage
                - features
                - preview
                - reviews
                - work_results
                - change_article
                - article
                - tech_instruction
                - category_description
            sheet_id: Индекс листа (0 = первый лист)
            from_row: Начальная строка (минимум 3)
            to_row: Конечная строка (-1 = до конца)
        
        Returns:
            {"status_code": 200, "detail": "success"}
        """
        payload = {
            "llm_model": llm_model,
            "link": link,
            "assistant": assistant,
            "sheet_id": sheet_id,
            "from_row": from_row,
            "to_row": to_row,
        }
        return await self._post("/process/google_sheet", payload)

    async def process_sheets(
        self,
        llm_model: str,
        link: str,
        name_sheet: dict[str, int],
    ) -> dict:
        """
        Обработка нескольких листов Google таблицы
        
        Args:
            llm_model: Модель OpenAI (например "gpt-4.1")
            link: URL Google таблицы
            name_sheet: Маппинг {assistant_name: sheet_id}
                Пример: {"description": 0, "usage": 1, "features": 2}
        
        Returns:
            {"status_code": 200, "detail": "success"}
        """
        payload = {
            "llm_model": llm_model,
            "link": link,
            "name_sheet": name_sheet,
        }
        return await self._post("/process/google_sheets", payload)

    # =========================================================================
    # Удобные методы для каждого типа ассистента
    # =========================================================================

    async def process_subdescription(
        self, llm_model: str, link: str, sheet_id: int = 0, from_row: int = 3, to_row: int = -1
    ) -> dict:
        """Обработка листа для краткого описания"""
        return await self.process_sheet(llm_model, link, "sub_description", sheet_id, from_row, to_row)

    async def process_description(
        self, llm_model: str, link: str, sheet_id: int = 0, from_row: int = 3, to_row: int = -1
    ) -> dict:
        """Обработка листа для полного описания"""
        return await self.process_sheet(llm_model, link, "description", sheet_id, from_row, to_row)

    async def process_usage(
        self, llm_model: str, link: str, sheet_id: int = 0, from_row: int = 3, to_row: int = -1
    ) -> dict:
        """Обработка листа для применения"""
        return await self.process_sheet(llm_model, link, "usage", sheet_id, from_row, to_row)

    async def process_features(
        self, llm_model: str, link: str, sheet_id: int = 0, from_row: int = 3, to_row: int = -1
    ) -> dict:
        """Обработка листа для свойств"""
        return await self.process_sheet(llm_model, link, "features", sheet_id, from_row, to_row)

    async def process_preview(
        self, llm_model: str, link: str, sheet_id: int = 0, from_row: int = 3, to_row: int = -1
    ) -> dict:
        """Обработка листа для превью"""
        return await self.process_sheet(llm_model, link, "preview", sheet_id, from_row, to_row)

    async def process_reviews(
        self, llm_model: str, link: str, sheet_id: int = 0, from_row: int = 3, to_row: int = -1
    ) -> dict:
        """Обработка листа для отзывов"""
        return await self.process_sheet(llm_model, link, "reviews", sheet_id, from_row, to_row)

    async def process_work_results(
        self, llm_model: str, link: str, sheet_id: int = 0, from_row: int = 3, to_row: int = -1
    ) -> dict:
        """Обработка листа для примеров работ"""
        return await self.process_sheet(llm_model, link, "work_results", sheet_id, from_row, to_row)

    async def process_change_article(
        self, llm_model: str, link: str, sheet_id: int = 0, from_row: int = 3, to_row: int = -1
    ) -> dict:
        """Обработка листа для рерайта статей"""
        return await self.process_sheet(llm_model, link, "change_article", sheet_id, from_row, to_row)

    async def process_article(
        self, llm_model: str, link: str, sheet_id: int = 0, from_row: int = 3, to_row: int = -1
    ) -> dict:
        """Обработка листа для создания статей"""
        return await self.process_sheet(llm_model, link, "article", sheet_id, from_row, to_row)

    async def process_tech_instruction(
        self, llm_model: str, link: str, sheet_id: int = 0, from_row: int = 3, to_row: int = -1
    ) -> dict:
        """Обработка листа для тех. инструкций"""
        return await self.process_sheet(llm_model, link, "tech_instruction", sheet_id, from_row, to_row)

    async def process_category_description(
        self, llm_model: str, link: str, sheet_id: int = 0, from_row: int = 3, to_row: int = -1
    ) -> dict:
        """Обработка листа для описаний категорий"""
        return await self.process_sheet(llm_model, link, "category_description", sheet_id, from_row, to_row)

