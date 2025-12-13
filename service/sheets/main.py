
import gspread
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from service.sheets.src.models import ProcessGoogleSheetRequest, ProcessGoogleSheetsRequest, ProcessResponse
from service.sheets.src.settings import logger
from service.sheets.src.utils import process_google_sheet, process_google_sheets

app = FastAPI(
    title="Politaks sheets API",
    version="0.0.1",
)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


@app.post(rout1:="/process/google_sheet", response_model=ProcessResponse)
async def process_google_sheet_endpoint(request: ProcessGoogleSheetRequest):
    """Эндпоинт для обработки одного листа Google таблицы."""
    try:
        await process_google_sheet(
            request.user_id,
            request.llm_model,
            request.link,
            request.assistant,
            request.sheet_id,
            request.from_row,
            request.to_row,
        )
    except gspread.exceptions.WorksheetNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Лист(ы) не найден(ы). Проверьте ID или название листа(ов): {e}",
        ) from None
    except gspread.exceptions.NoValidUrlKeyFound as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Некорректная ссылка на таблицу. Не удалось найти ключ (ID) таблицы: {e}",
        ) from None
    except (gspread.exceptions.IncorrectCellLabel, gspread.exceptions.InvalidInputValue) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Некорректные данные ячейки или диапазона: {e}",
        ) from None
    except gspread.exceptions.GSpreadException as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Ошибка взаимодействия с api Google Sheets: {e}",
        ) from None
    except HTTPException as e:
        if f"Error - {rout1}" in e.detail:
            logger.error(e.detail)
        else:
            logger.error(f"Error - {rout1} - {e.detail}")
        raise
    except Exception as e:
        logger.exception(f"Exception {rout1} - {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Exception {rout1} - {e}") from e
    else:
        return ProcessResponse(status_code=status.HTTP_200_OK, detail="success")


@app.post(rout2:="/process/google_sheets", response_model=ProcessResponse)
async def process_google_sheets_endpoint(request: ProcessGoogleSheetsRequest):
    """Эндпоинт для обработки всей Google таблицы."""
    try:
        await process_google_sheets(
            request.user_id,
            request.llm_model,
            request.link,
            request.name_sheet,
        )
    except gspread.exceptions.WorksheetNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Лист(ы) не найден(ы). Проверьте ID или название листа(ов): {e}",
        ) from None
    except gspread.exceptions.NoValidUrlKeyFound as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Некорректная ссылка на таблицу. Не удалось найти ключ (ID) таблицы: {e}",
        ) from None
    except (gspread.exceptions.IncorrectCellLabel, gspread.exceptions.InvalidInputValue) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Некорректные данные ячейки или диапазона: {e}",
        ) from None
    except gspread.exceptions.GSpreadException as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Ошибка взаимодействия с api Google Sheets: {e}",
        ) from None
    except HTTPException as e:
        if f"Error - {rout2}" in e.detail:
            logger.error(e.detail)
        else:
            logger.error(f"Error - {rout2} - {e.detail}")
        raise
    except Exception as e:
        logger.exception(f"Exception {rout2} - {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Exception {rout2} - {e}") from e
    else:
        return ProcessResponse(status_code=status.HTTP_200_OK, detail="success")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("service.sheets.main:app", host="0.0.0.0", port=7998, workers=2)
