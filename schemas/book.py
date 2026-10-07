from models.book import BookType
from pydantic import BaseModel, Field, ConfigDict, model_validator

class BookCreate(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        max_length=255
    )

    isbn: str | None = Field(
        default=None,
        min_length=10,
        max_length=20
    )

    book_type: BookType = BookType.PHYSICAL

    total_copies: int = Field(
        default=1,
        ge=1,
        le=100000
    )

    available_copies: int = Field(
        default=1,
        ge=0,
        le=100000
    )

    file_path: str | None = Field(
        default=None,
        max_length=500
    )

    description: str | None = Field(
        default=None,
        max_length=5000
    )

    published_year: int | None = Field(
        default=None,
        ge=1000,
        le=2026
    )
    @model_validator(mode="after")
    def validate_copies(self):
        if self.available_copies > self.total_copies:
            raise ValueError(
                "available_copies cannot be greater than total_copies"
            )

        return self


class BookUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255
    )

    isbn: str | None = Field(
        default=None,
        min_length=10,
        max_length=20
    )

    book_type: BookType | None = None

    total_copies: int | None = Field(
        default=None,
        ge=1,
        le=100000
    )

    available_copies: int | None = Field(
        default=None,
        ge=0,
        le=100000
    )

    file_path: str | None = Field(
        default=None,
        max_length=500
    )

    description: str | None = Field(
        default=None,
        max_length=5000
    )

    published_year: int | None = Field(
        default=None,
        ge=1000,
        le=2026
    )

    is_active: bool | None = None

    @model_validator(mode="after")
    def validate_copies(self):

        if (
            self.total_copies is not None
            and self.available_copies is not None
            and self.available_copies > self.total_copies
        ):
            raise ValueError(
                "available_copies cannot be greater than total_copies"
            )

        return self


class BookResponse(BaseModel):
    id: int
    title: str
    isbn: str | None
    book_type: BookType
    total_copies: int
    available_copies: int
    file_path: str | None
    description: str | None
    published_year: int | None
    is_active: bool

    model_config = ConfigDict(
        from_attributes=True
    )