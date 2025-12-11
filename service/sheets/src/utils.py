
import asyncio
import json

import aiohttp
import gspread

from service.assistants.src.llm_utils import OpenAIAgent

from .settings import DJANGO_API_URL, GOOGLE_SH_CREDS, logger

gc = gspread.service_account_from_dict(GOOGLE_SH_CREDS)
agent = OpenAIAgent()
assistant_func = {
    "sub_description": agent.get_sub_description,
    "description": agent.get_description,
    "usage": agent.get_usage,
    "features": agent.get_features,
    "preview": agent.get_preview,
    "reviews": agent.get_reviews,
    "work_results": agent.get_work_results,
    "change_article": agent.change_article,
    "articele": agent.get_article,
    "tech_instruction": agent.change_tech_instruction,
    "category_description": agent.change_category_description,
}


async def _save_process_data(record: dict, user_id: str, llm_model: str, assistant: str, result: str, idx: int):
    record.popitem()
    parameters = [
        {"name": k, "value": v} for k, v in record.items()
    ]
    domain = record.get("Домен (url)", "")

    payload = {
        "parametrs": json.dumps(parameters, ensure_ascii=False),
        "domen": str(domain),
        "html": str(result),
        "user": str(user_id),
        "model": str(llm_model),
        "assistant": str(assistant),
        "source": "excel",
    }

    async with aiohttp.ClientSession() as session, session.post(f"{DJANGO_API_URL}/api/response/save", json=payload) as resp:
        if resp.status != 200:
            error_text = await resp.text()
            logger.error(f"_save_process_data() - Failed for '{assistant}' row={idx}: {resp.status} - {error_text}")


async def process_google_sheet(user_id: str, llm_model: str, link: str, assistant: str, sheet_id: int, from_row: int, to_row: int):
    from_row = max(from_row-2, 1)
    spreadsheet = gc.open_by_url(link)
    worksheet = spreadsheet.get_worksheet(sheet_id)

    wsh_records: list[dict] = worksheet.get_all_records()
    wsh_records = wsh_records[from_row:to_row] if to_row != -1 else wsh_records[from_row:]
    # logger.debug(wsh_records)
    headers = worksheet.row_values(1)
    result_col_index = headers.index("Результат") + 1
    result_col_data = worksheet.col_values(result_col_index)

    async def handle_row(idx: int, record: dict):
        try:
            # logger.debug(f"process_google_sheet() - {assistant} - request_sended for row {idx}")
            args = list(record.values())[:-1]
            result = await assistant_func[assistant](llm_model, *args)
            worksheet.update_cell(idx, result_col_index, result)
            await _save_process_data(record, user_id, llm_model, assistant, result, idx)
        except Exception as e:
            logger.error(f"process_google_sheet().handle_row() - {assistant} - row {idx} - {e}")

    tasks_data = [
        (i, record) for i, record in enumerate(wsh_records, from_row+2)
        if result_col_data[i] and len(str(result_col_data[i])) < 6
    ]

    batch_size = 3
    for i in range(0, len(tasks_data), batch_size):
        batch = tasks_data[i:i + batch_size]
        current_tasks = [
            asyncio.create_task(handle_row(idx, rec))
            for idx, rec in batch
        ]
        await asyncio.gather(*current_tasks)
        if i + batch_size < len(tasks_data):
            await asyncio.sleep(20)


async def process_google_sheets(user_id: str, llm_model: str, link: str, name_sheet: dict[str, int]):
    tasks = [
        asyncio.create_task(
            process_google_sheet(
                user_id=user_id,
                llm_model=llm_model,
                assistant=assistant_name,
                link=link,
                sheet_id=sheet_id,
                from_row=3,
                to_row=-1,
            ),
        )
        for assistant_name, sheet_id in name_sheet.items()
    ]
    await asyncio.gather(*tasks)
