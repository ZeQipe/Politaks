
import base64
import json
import time

import httpx
from openai import AsyncOpenAI

from .llm_instructions import *
from .models import ReviewsResponse
from .other_utils import get_products_links, get_related_products
from .settings import LOGS_DIR, OPENAI_API_KEY, PROXY, logger


class OpenAIAgent:
    def __init__(self):
        _http_client = httpx.AsyncClient(proxy=PROXY if PROXY else None)
        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY, http_client=_http_client)


    async def get_llm_answer(self,
        instruction: str|None=None, prompt: str|None=None, text_format=None,
        model: str="gpt-4.1", temperature: float|None = None,
    ):
        """Функция для отправки запроса в OpenAI API."""
        try:
            logger.info(f"get_llm_answer() PROMPT = {prompt}")
            if text_format:
                response = await self.client.responses.parse(
                    input=prompt,
                    model=model,
                    text_format=text_format,
                    instructions=instruction,
                    store=False,
                    temperature=temperature,
                )
            else:
                response = await self.client.responses.create(
                    input=prompt,
                    model=model,
                    instructions=instruction,
                    store=False,
                    temperature=temperature,
                )

        except Exception as e:
            logger.error(f"Exception get_llm_answer() - {e}")
            raise
        else:
            return response


    async def get_sub_description(self, llm_model: str, domain: str, product_name: str, description: str, usage: str,
        seo_high_freq: str, seo_medium_freq: str, seo_low_freq: str,
    ) -> str:
        related_products = await get_related_products(domain, [product_name])
        prompt = f"<seo_high_freq>\nВЧ:\n{seo_high_freq}\n</seo_high_freq>"
        prompt = f"{prompt}\n<seo_medium_freq>\nСЧ:\n{seo_medium_freq}\n</seo_medium_freq>"
        prompt = f"{prompt}\n<seo_low_freq>\nНЧ:\n{seo_low_freq}\n</seo_low_freq>"
        prompt = f"{prompt}\n\n<description>\nОписание:\n{description}\n</description>"
        prompt = f"{prompt}\n<usage>\nПрименение:\n{usage}\n</usage>"
        if related_products:
            prompt = f"{prompt}\n<related_products>\nСвязанные товары:\n{related_products}</related_products>"

        temp_response = await self.get_llm_answer(subdescription_instruction, prompt, model=llm_model)
        response_output = await self.negative_prompt(llm_model, temp_response.output_text)

        await self.log_to_file("get_sub_description_log", temp_response)

        return response_output.replace("\n", "")


    async def get_description(self, llm_model: str, domain: str, product_name: str, description: str, usage: str,
        seo_high_freq: str, seo_medium_freq: str, seo_low_freq: str,
    ) -> str:
        related_products = await get_related_products(domain, [product_name])
        prompt = f"<seo_high_freq>\nВЧ:\n{seo_high_freq}\n</seo_high_freq>"
        prompt = f"{prompt}\n<seo_medium_freq>\nСЧ:\n{seo_medium_freq}\n</seo_medium_freq>"
        prompt = f"{prompt}\n<seo_low_freq>\nНЧ:\n{seo_low_freq}\n</seo_low_freq>"
        prompt = f"{prompt}\n\n<description>\nОписание:\n{description}\n</description>"
        if usage:
            prompt = f"{prompt}\n<usage>\nПрименение:\n{usage}\n</usage>"
        if related_products:
            prompt = f"{prompt}\n<related_products>\nСвязанные товары:\n{related_products}</related_products>"

        temp_response = await self.get_llm_answer(description_instruction, prompt, model=llm_model)
        response_output = await self.negative_prompt(llm_model, temp_response.output_text)

        await self.log_to_file("get_description_log", temp_response)

        return response_output.replace("\n", "")


    async def negative_prompt(self, llm_model: str, result: str) -> str:
        prompt = f"Полученный результат:\n{result}"
        response = await self.get_llm_answer(negative_instruction, prompt, model=llm_model)

        await self.log_to_file("negative_prompt_log", response)

        return response.output_text


    async def get_usage(self, llm_model: str, domain: str, product_name: str, usage: str) -> str:
        # related_products = await get_related_products(domain, [product_name])
        prompt = f"<usage>\nПрименение:\n{usage}\n</usage>"
        # if related_products:
        #     prompt = f"{prompt}\n<related_products>\nСвязанные товары:\n{related_products}</related_products>"
        response = await self.get_llm_answer(usage_instruction, prompt, model=llm_model)

        await self.log_to_file("get_usage_log", response)

        return response.output_text#.replace("\n", "")


    async def get_features(self, llm_model: str, domain: str, product_name: str, features: str) -> str:
        # related_products = await get_related_products(domain, [product_name])
        prompt = f"<features>\nСвойства:\n{features}\n</features>"
        # if related_products:
        #     prompt = f"{prompt}\n<related_products>\nСвязанные товары:\n{related_products}</related_products>"
        response = await self.get_llm_answer(features_instruction, prompt, model=llm_model)

        await self.log_to_file("get_features_log", response)

        return response.output_text


    async def get_preview(self, llm_model: str, domain: str, product_name: str, description: str, usage: str,
        seo_high_freq: str, seo_medium_freq: str, seo_low_freq: str,
    ) -> str:
        related_products = await get_related_products(domain, [product_name])
        prompt = f"<seo_high_freq>\nВЧ:\n{seo_high_freq}\n</seo_high_freq>"
        prompt = f"{prompt}\n<seo_medium_freq>\nСЧ:\n{seo_medium_freq}\n</seo_medium_freq>"
        prompt = f"{prompt}\n<seo_low_freq>\nНЧ:\n{seo_low_freq}\n</seo_low_freq>"
        prompt = f"{prompt}\n\n<description>\nОписание:\n{description}\n</description>"
        if usage:
            prompt = f"{prompt}\n<usage>\nПрименение:\n{usage}\n</usage>"
        if related_products:
            prompt = f"{prompt}\n<related_products>\nСвязанные товары:\n{related_products}</related_products>"
        response = await self.get_llm_answer(preview_instruction, prompt, model=llm_model)

        await self.log_to_file("get_previews_log", response)

        return response.output_text


    async def get_reviews(self, llm_model: str, product_name: str, description: str, usage: str,
        seo_high_freq: str, seo_medium_freq: str, seo_low_freq: str,
    ) -> list[str]:
        prompt = f"<seo_high_freq>\nВЧ:\n{seo_high_freq}\n</seo_high_freq>"
        prompt = f"{prompt}\n<seo_medium_freq>\nСЧ:\n{seo_medium_freq}\n</seo_medium_freq>"
        prompt = f"{prompt}\n<seo_low_freq>\nНЧ:\n{seo_low_freq}\n</seo_low_freq>"
        prompt = f"{prompt}\n\n<product_name>\nНазвание товара:\n{product_name}\n</product_name>"
        prompt = f"{prompt}\n<description>\nОписание:\n{description}\n</description>"
        if usage:
            prompt = f"{prompt}\n<usage>\nПрименение:\n{usage}\n</usage>"

        response = await self.get_llm_answer(review_instruction, prompt, text_format=ReviewsResponse, model=llm_model)

        await self.log_to_file("get_reviews_log", response)

        return json.loads(response.output_text)


    async def get_work_results(self, llm_model: str, domain: str,
        place_name: str, location: str, background_info: str,
        products_name: str, descriptions: str,
        photo1: bytes, photo2: bytes,
    ) -> str:
        products_links = await get_products_links(domain, [name.strip() for name in products_name.split(",")])
        prompt = f"<place_name>\nНазвание места/объекта:\n{place_name}\n</place_name>"
        prompt = f"{prompt}\n\n<location>\nРасположение:\n{location}\n</location>"
        prompt = f"{prompt}\n\n<background_info>\nДополнительная информация:\n{background_info}\n</background_info>"
        prompt = f"{prompt}\n\n<used_products>\nИспользованные товары:\n{products_links}\n</used_products>"
        prompt = f"{prompt}\n\n<descriptions>\nОписания использованных товаров:\n{descriptions}\n</descriptions>"
        content = [{ "type": "input_text", "text": prompt }]

        if photo1:
            b64_image1 = base64.b64encode(photo1).decode("utf-8")
            content.append(
                {
                    "type": "input_image",
                    "image_url": f"data:image/jpeg;base64,{b64_image1}",
                },
            )
        if photo2:
            b64_image2 = base64.b64encode(photo2).decode("utf-8")
            content.append(
                {
                    "type": "input_image",
                    "image_url": f"data:image/jpeg;base64,{b64_image2}",
                },
            )

        prompt = [{
            "role": "user",
            "content": content,
        }]

        response = await self.get_llm_answer(work_results_instruction, prompt, model=llm_model)

        await self.log_to_file("get_work_results_log", response)

        return response.output_text


    async def change_article(self, llm_model: str, title: str, article: str,
        seo_high_freq: str, seo_medium_freq: str, seo_low_freq: str,
    ) -> str:
        prompt = f"<seo_high_freq>\nВЧ:\n{seo_high_freq}\n</seo_high_freq>"
        prompt = f"{prompt}\n<seo_medium_freq>\nСЧ:\n{seo_medium_freq}\n</seo_medium_freq>"
        prompt = f"{prompt}\n<seo_low_freq>\nНЧ:\n{seo_low_freq}\n</seo_low_freq>"
        prompt = f"{prompt}\n\n<title>\nНазвание статьи:\n{title}\n</title>"
        prompt = f"{prompt}\n<article>\nСтатья:\n{article}\n</article>"

        response = await self.get_llm_answer(ch_article_instruction, prompt, model=llm_model)

        await self.log_to_file("change_article_log", response)

        return response.output_text


    async def get_article(self, llm_model: str, topic: str, comment: str,
        seo_high_freq: str, seo_medium_freq: str, seo_low_freq: str,
    ) -> str:
        prompt = f"<seo_high_freq>\nВЧ:\n{seo_high_freq}\n</seo_high_freq>"
        prompt = f"{prompt}\n<seo_medium_freq>\nСЧ:\n{seo_medium_freq}\n</seo_medium_freq>"
        prompt = f"{prompt}\n<seo_low_freq>\nНЧ:\n{seo_low_freq}\n</seo_low_freq>"
        prompt = f"{prompt}\n<topic>\nТема:\n{topic}\n</topic>"
        prompt = f"{prompt}\n<comment>\nКомментарий:\n{comment}\n</comment>"

        response = await self.get_llm_answer(article_instruction, prompt, model=llm_model)

        await self.log_to_file("get_article_log", response)

        return response.output_text


    async def change_tech_instruction(self, llm_model: str, domain: str, tech_instruction: str,
        seo_high_freq: str, seo_medium_freq: str, seo_low_freq: str,
    ) -> str:
        products_links = await get_products_links(domain, ["_all"])
        prompt = f"<seo_high_freq>\nВЧ:\n{seo_high_freq}\n</seo_high_freq>"
        prompt = f"{prompt}\n<seo_medium_freq>\nСЧ:\n{seo_medium_freq}\n</seo_medium_freq>"
        prompt = f"{prompt}\n<seo_low_freq>\nНЧ:\n{seo_low_freq}\n</seo_low_freq>"
        prompt = f"{prompt}\n<tech_instruction>\nТехническая инструкция:\n{tech_instruction}\n</tech_instruction>"
        prompt = f"{prompt}\n<products_links>\nСсылки на товары:\n{products_links}\n</products_links>"
        response = await self.get_llm_answer(tech_instruction_instruction, prompt, model=llm_model)

        await self.log_to_file("change_tech_instruction_log", response)

        return response.output_text


    async def change_category_description(self, llm_model: str, domain: str, category_description: str,
        seo_high_freq: str, seo_medium_freq: str, seo_low_freq: str,
    ) -> str:
        products_links = await get_products_links(domain, ["_all"])
        prompt = f"<seo_high_freq>\nВЧ:\n{seo_high_freq}\n</seo_high_freq>"
        prompt = f"{prompt}\n<seo_medium_freq>\nСЧ:\n{seo_medium_freq}\n</seo_medium_freq>"
        prompt = f"{prompt}\n<seo_low_freq>\nНЧ:\n{seo_low_freq}\n</seo_low_freq>"
        prompt = f"{prompt}\n<category_description>\nОписание в (под)категории:\n{category_description}\n</category_description>"
        prompt = f"{prompt}\n<products_links>\nСсылки на товары:\n{products_links}\n</products_links>"
        response = await self.get_llm_answer(category_description_instruction, prompt, model=llm_model)

        await self.log_to_file("change_category_description_log", response)

        return response.output_text


    async def correct_result(self, llm_model: str, result: str, facts: str) -> str:
        prompt = f"Полученный результат:\n{result}\n\n---\n\nФакты:\n{facts}"
        response = await self.get_llm_answer(correct_res_instruction, prompt, model=llm_model)

        await self.log_to_file("correct_res_log", response)

        return response.output_text


    async def log_to_file(self, file_name: str, response) -> None:
        header = f"[{time.strftime('%Y-%m-%d %H:%M:%S')} LOG]"
        buffer = (str(res) for res in response)
        with open(LOGS_DIR / f"{file_name}.log", "a", encoding="utf-8") as f:
            f.write(f"{header}\n{'\n'.join(buffer)}\n\n")
