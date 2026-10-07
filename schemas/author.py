from pydantic import BaseModel, Field, ConfigDict


class AuthorCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=150
    )


class AuthorUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150
    )


class AuthorResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(
        from_attributes=True
    )