
from pydantic import BaseModel, Field


class ProcessGoogleSheetsRequest(BaseModel):
    user_id: str
    llm_model: str
    link: str
    name_sheet: dict[str, int]

class ProcessGoogleSheetRequest(BaseModel):
    user_id: str
    llm_model: str
    link: str
    assistant: str
    sheet_id: int
    from_row: int = Field(default=3, ge=3)
    to_row: int = Field(default=-1, ge=-1)

class ProcessResponse(BaseModel):
    status_code: int
    detail: str
