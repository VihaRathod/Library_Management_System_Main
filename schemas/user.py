from pydantic import BaseModel, EmailStr, Field, ConfigDict

from models.user import UserRole


class UserCreate(BaseModel):
    email: EmailStr

    password: str = Field(
        ...,
        min_length=8,
        max_length=50
    )

    name: str = Field(
        ...,
        min_length=2,
        max_length=150
    )

    phone: str | None = Field(
        default=None,
        min_length=7,
        max_length=20
    )


class UserUpdate(BaseModel):
    email: EmailStr | None = None

    password: str | None = Field(
        default=None,
        min_length=8,
        max_length=50
    )

    role: UserRole | None = None

    is_active: bool | None = None


class UserSelfUpdate(BaseModel):
    email: EmailStr | None = None

    password: str | None = Field(
        default=None,
        min_length=8,
        max_length=50
    )


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: UserRole
    is_active: bool

    model_config = ConfigDict(
        from_attributes=True
    )