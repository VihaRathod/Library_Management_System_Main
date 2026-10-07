from pydantic import BaseModel, Field, ConfigDict


class CourseCreate(BaseModel):
    code: str = Field(
        ...,
        min_length=1,
        max_length=50
    )

    title: str = Field(
        ...,
        min_length=1,
        max_length=255
    )

    description: str | None = Field(
        default=None,
        max_length=2000
    )


class CourseUpdate(BaseModel):
    code: str | None = Field(
        default=None,
        min_length=1,
        max_length=50
    )

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255
    )

    description: str | None = Field(
        default=None,
        max_length=2000
    )

    is_active: bool | None = None


class CourseResponse(BaseModel):
    id: int
    code: str
    title: str
    description: str | None
    is_active: bool

    model_config = ConfigDict(
        from_attributes=True
    )