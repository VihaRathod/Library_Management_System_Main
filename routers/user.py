from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.connection import get_db

from dependencies.auth import (
    get_current_user,
    require_role,
)
from fastapi import Query

from models.user import User, UserRole
from schemas.pagination import PageResponse
from models.user import User, UserRole

from schemas.user import (
    UserCreate,
    UserUpdate,
    UserSelfUpdate,
    UserResponse,
)

from services.user_service import (
    create_user,
    get_users,
    get_user,
    update_user,
    delete_user,
)


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# --------------------------------------------------
# CREATE USER / REGISTER
# --------------------------------------------------

# @router.post(
#     "/",
#     response_model=UserResponse,
#     status_code=status.HTTP_201_CREATED
# )
# def create(
#     user_data: UserCreate,
#     db: Session = Depends(get_db)
# ):
#     """
#     Public registration endpoint.

#     Every newly registered user becomes a MEMBER.
#     The client cannot choose the role.
#     """

#     user, error = create_user(
#         db,
#         user_data
#     )

#     if error:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=error
#         )

#     return user


# --------------------------------------------------
# GET ALL USERS
# LIBRARIAN ONLY
# --------------------------------------------------

@router.get(
    "/",
    response_model=PageResponse[UserResponse]
)
def get_all(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),

    email: str | None = Query(None),
    role: UserRole | None = Query(None),
    is_active: bool | None = Query(None),

    sort: str | None = Query(None),

    db: Session = Depends(get_db),

    current_user: User = Depends(
        require_role(UserRole.LIBRARIAN)
    )
):

    return get_users(
        db=db,
        page=page,
        limit=limit,
        email=email,
        role=role,
        is_active=is_active,
        sort=sort
    )

# --------------------------------------------------
# GET CURRENT USER
# AUTHENTICATED USERS
# --------------------------------------------------

@router.get(
    "/me",
    response_model=UserResponse
)
def get_me(
    current_user: User = Depends(get_current_user)
):
    """
    Get the currently logged-in user's profile.
    """

    return current_user


# --------------------------------------------------
# UPDATE CURRENT USER
# AUTHENTICATED USERS
# --------------------------------------------------

@router.put(
    "/me",
    response_model=UserResponse
)
def update_me(
    user_data: UserSelfUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Users can update only their own email/password.
    They cannot change:
    - role
    - is_active
    """

    user, error = update_user(
        db,
        current_user.id,
        user_data
    )

    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    return user


# --------------------------------------------------
# GET USER BY ID
# LIBRARIAN ONLY
# --------------------------------------------------

@router.get(
    "/{user_id}",
    response_model=UserResponse
)
def get_one(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.LIBRARIAN)
    )
):
    """
    Only librarians can view another user's details.
    """

    user = get_user(
        db,
        user_id
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


# --------------------------------------------------
# UPDATE USER BY ID
# LIBRARIAN ONLY
# --------------------------------------------------

@router.put(
    "/{user_id}",
    response_model=UserResponse
)
def update(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.LIBRARIAN)
    )
):
    """
    Librarian can update another user's:
    - email
    - password
    - role
    - active status
    """

    # Optional safety check:
    # prevent librarian from deactivating themselves
    if (
        user_id == current_user.id
        and user_data.is_active is False
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot deactivate yourself"
        )

    user, error = update_user(
        db,
        user_id,
        user_data
    )

    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


# --------------------------------------------------
# DELETE / DEACTIVATE USER
# LIBRARIAN ONLY
# --------------------------------------------------

@router.delete(
    "/{user_id}"
)
def delete(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.LIBRARIAN)
    )
):
    """
    Deactivates a user instead of physically
    deleting the database record.
    """

    # Prevent librarian from deactivating themselves
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot deactivate yourself"
        )

    user = delete_user(
        db,
        user_id
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return {
        "message": "User deactivated successfully"
    }