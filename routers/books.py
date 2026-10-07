from fastapi import APIRouter, Depends, HTTPException, status,Query
from sqlalchemy.orm import Session
from dependencies.auth import get_current_user,require_role

from database.connection import get_db
from models.user import UserRole
from models.user import User
from schemas.book import (
    BookCreate,
    BookUpdate,
    BookResponse
)
from schemas.pagination import PageResponse

from services.book_service import (
    create_book,
    get_books,
    get_book,
    update_book,
    delete_book
)


router = APIRouter(
    prefix="/books",
    tags=["Books"]
)


@router.post(
    "/",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED
)
def create(
    book_data: BookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.LIBRARIAN)
    )
):
    return create_book(
        db,
        book_data
    )


@router.get(
    "/",
    response_model=PageResponse[BookResponse]
)
def get_all(
    page: int = Query(
        1,
        ge=1
    ),

    limit: int = Query(
        10,
        ge=1,
        le=100
    ),

    title: str | None = Query(
        None
    ),

    author: str | None = Query(
        None
    ),

    available: bool | None = Query(
        None
    ),

    sort: str | None = Query(
        None
    ),

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    return get_books(
        db=db,
        page=page,
        limit=limit,
        title=title,
        author=author,
        available=available,
        sort=sort
    )


@router.get(
    "/{book_id}",
    response_model=BookResponse
)
def get_one(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):
    book = get_book(
        db,
        book_id
    )

    if not book:
        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )

    return book


@router.put(
    "/{book_id}",
    response_model=BookResponse
)
def update(
    book_id: int,
    book_data: BookUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.LIBRARIAN)
    )
):
    try:
        book = update_book(
            db,
            book_id,
            book_data
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    if not book:
        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )

    return book


@router.delete(
    "/{book_id}"
)
def delete(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.LIBRARIAN)
    )
):
    book = delete_book(
        db,
        book_id
    )

    if not book:
        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )

    return {
        "message": "Book deleted successfully"
    }