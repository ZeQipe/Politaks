
import asyncio

import gspread

from service.assistants.src.llm_utils import OpenAIAgent

from .settings import GOOGLE_SH_CREDS, logger

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


async def process_google_sheet(llm_model: str, link: str, assistant: str, sheet_id: int, from_row: int, to_row: int):
    from_row = max(from_row-2, 1)
    spreadsheet = gc.open_by_url(link)
    worksheet = spreadsheet.get_worksheet(sheet_id)

    wsh_records: list[dict] = worksheet.get_all_records()
    wsh_records = wsh_records[from_row:to_row] if to_row != -1 else wsh_records[from_row:]
    # logger.debug(wsh_records)
    header = worksheet.row_values(1)
    result_col_index = header.index("Результат") + 1
    async_req_num = 50

    async def handle_row(idx: int, record: dict):
        try:
            # logger.debug(f"process_google_sheet() - {assistant} - request_sended for row {idx}")
            args = list(record.values())[:-1]
            async with asyncio.Semaphore(async_req_num):
                result = await assistant_func[assistant](llm_model, *args)
            worksheet.update_cell(idx, result_col_index, result)
        except Exception as e:
            logger.error(f"process_google_sheet().handle_row() - {assistant} - row {idx} - {e}")
    tasks = [
        asyncio.create_task(handle_row(i, record))
        for i, record in enumerate(wsh_records, from_row+2)
    ]
    await asyncio.gather(*tasks)


async def process_google_sheets(llm_model: str, link: str, name_sheet: dict[str, int]):
    tasks = [
        asyncio.create_task(
            process_google_sheet(
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
