from datetime import date

from pydantic import BaseModel, Field, ConfigDict
from typing import Literal

from models.loan import LoanStatus


class LoanCreate(BaseModel):

    user_id: int = Field(
        ...,
        gt=0
    )

    book_id: int = Field(
        ...,
        gt=0
    )


class LoanUpdate(BaseModel):
    status: LoanStatus | None = None
    return_date: date | None = None

class LoanResponse(BaseModel):

    id: int
    user_id: int
    book_id: int
    issue_date: date
    due_date: date
    return_date: date | None
    status: LoanStatus
    receipt_path: str | None

    model_config = ConfigDict(
        from_attributes=True
    )