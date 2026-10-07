from typing import Generic, TypeVar

from pydantic import BaseModel


T = TypeVar("T")


class PageResponse(
    BaseModel,
    Generic[T]
):

    page_number: int
    page_size: int
    total_pages: int
    total_record: int
    content: list[T]