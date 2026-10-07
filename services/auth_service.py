from sqlalchemy.orm import Session

from models.user import User

from utils.password import verify_password
from utils.jwt import create_access_token


def authenticate_user(
    db: Session,
    email: str,
    password: str
):

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not user:
        return None

    if not verify_password(
        password,
        user.password_hash
    ):
        return None

    if not user.is_active:
        return None

    return user


def login_user(
    db: Session,
    email: str,
    password: str
):

    user = authenticate_user(
        db,
        email,
        password
    )

    if not user:
        return None

    token = create_access_token(
        user.id
    )

    return token