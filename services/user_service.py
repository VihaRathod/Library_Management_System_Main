from datetime import date

from sqlalchemy.orm import Session

from models.user import User, UserRole

from schemas.user import (
    UserCreate,
    UserUpdate
)

from utils.password import hash_password

from sqlalchemy.orm import Session

from models.user import User, UserRole

from utils.query import (
    apply_filter,
    apply_sort,
    paginate_query
)


USER_SORT_FIELDS = {
    "id",
    "email",
    "role"
}
USER_FILTER_FIELDS = {
    "email"
}
def create_user(
    db: Session,
    user_data: UserCreate
):

    existing_user = (
        db.query(User)
        .filter(
            User.email == user_data.email
        )
        .first()
    )

    if existing_user:
        return None, "Email already registered"

    try:

        user = User(
            email=user_data.email,
            password_hash=hash_password(
                user_data.password
            ),
            role=UserRole.MEMBER,
            is_active=True
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user, None

    except Exception as e:

        db.rollback()

        return None, str(e)



def get_users(
    db: Session,
    page: int = 1,
    limit: int = 10,
    email: str | None = None,
    role: UserRole | None = None,
    is_active: bool | None = None,
    sort: str | None = None
):

    query = db.query(User)

    query = db.query(User)

    query = apply_filter(
        query,
        User,
        {
            "email": email
        },
        USER_FILTER_FIELDS
    )

    if role is not None:
        query = query.filter(
            User.role == role
        )

    if is_active is not None:
        query = query.filter(
            User.is_active == is_active
        )

    query = apply_sort(
        query,
        User,
        sort,
        USER_SORT_FIELDS
    )

    return paginate_query( 
        query,
        page,
        limit
    )


def get_user(
    db: Session,
    user_id: int
):
    return (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )


def update_user(
    db: Session,
    user_id: int,
    user_data: UserUpdate
):

    user = get_user(
        db,
        user_id
    )

    if not user:
        return None, "User not found"

    update_data = user_data.model_dump(
        exclude_unset=True
    )

    if "password" in update_data:

        user.password_hash = hash_password(
            update_data.pop("password")
        )

    if "email" in update_data:

        existing = (
            db.query(User)
            .filter(
                User.email == update_data["email"],
                User.id != user_id
            )
            .first()
        )

        if existing:
            return None, "Email already registered"

    for field, value in update_data.items():
        setattr(
            user,
            field,
            value
        )

    db.commit()
    db.refresh(user)

    return user, None


def delete_user(
    db: Session,
    user_id: int
):

    user = get_user(
        db,
        user_id
    )

    if not user:
        return None

    # Soft delete / deactivate
    user.is_active = False

    db.commit()
    db.refresh(user)

    return user