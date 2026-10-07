from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database.connection import get_db

from schemas.author import (
    AuthorCreate,
    AuthorUpdate,
    AuthorResponse
)
from dependencies.auth import get_current_user,require_role
from models.user import User, UserRole
from schemas.pagination import PageResponse
from services.author_service import (
    create_author,
    get_authors,
    get_author,
    update_author,
    delete_author
)


router = APIRouter(
    prefix="/authors",
    tags=["Authors"]
)


@router.post(
    "/",
    response_model=AuthorResponse,
    status_code=status.HTTP_201_CREATED
)
def create(
    author_data: AuthorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.LIBRARIAN)
    )
):
    return create_author(
        db,
        author_data
    )


@router.get(
    "/",
    response_model=PageResponse[AuthorResponse]
)
def get_all(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),

    name: str | None = Query(None),
    sort: str | None = Query(None),

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    return get_authors(
        db=db,
        page=page,
        limit=limit,
        name=name,
        sort=sort
    )


@router.get(
    "/{author_id}",
    response_model=AuthorResponse
)
def get_one(
    author_id: int,
    db: Session = Depends(get_db),
        current_user: User = Depends(
            get_current_user
        )
):
    author = get_author(
        db,
        author_id
    )

    if not author:
        raise HTTPException(
            status_code=404,
            detail="Author not found"
        )

    return author


@router.put(
    "/{author_id}",
    response_model=AuthorResponse
)
def update(
    author_id: int,
    author_data: AuthorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.LIBRARIAN)
    )
):
    author = update_author(
        db,
        author_id,
        author_data
    )

    if not author:
        raise HTTPException(
            status_code=404,
            detail="Author not found"
        )

    return author


@router.delete(
    "/{author_id}"
)
def delete(
    author_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.LIBRARIAN)
    )
):
    author = delete_author(
        db,
        author_id
    )

    if not author:
        raise HTTPException(
            status_code=404,
            detail="Author not found"
        )

    return {
        "message": "Author deleted successfully"
    }