from sqlalchemy import or_
from sqlalchemy.orm import Session

from models.book import Book
from models.author import Author
from schemas.book import BookCreate, BookUpdate

from utils.query import (
    apply_filter,
    apply_sort,
    paginate_query
)


BOOK_SORT_FIELDS = {
    "id",
    "title",
    "isbn",
    "book_type",
    "total_copies",
    "available_copies",
    "published_year"
}
BOOK_FILTER_FIELDS = {
    "title"
}

def create_book(
    db: Session,
    book_data: BookCreate
):
    book = Book(
        **book_data.model_dump()
    )

    db.add(book)
    db.commit()
    db.refresh(book)

    return book


def get_books(
    db: Session,
    page: int = 1,
    limit: int = 10,
    title: str | None = None,
    author: str | None = None,
    available: bool | None = None,
    sort: str | None = None
):

    query = db.query(Book).filter(
        Book.is_active == True
    )

    query = apply_filter(
        query,
        Book,
        {
            "title": title
        },
        BOOK_FILTER_FIELDS
    )

    if author:
        query = (
            query
            .join(Book.authors)
            .filter(
                Author.name.ilike(f"%{author}%")
            )
            .distinct()
        )

    if available is True:
        query = query.filter(
            Book.available_copies > 0
        )
    elif available is False:
        query = query.filter(
            Book.available_copies == 0
        )

    # Sorting
    query = apply_sort(
        query,
        Book,
        sort,
        BOOK_SORT_FIELDS
    )

    # Pagination
    return paginate_query(
        query,
        page,
        limit
    )


def get_book(
    db: Session,
    book_id: int
):
    return (
        db.query(Book)
        .filter(Book.id == book_id, Book.is_active == True)
        .first()
    )


def update_book(
    db: Session,
    book_id: int,
    book_data: BookUpdate
):
    book = get_book(db, book_id)

    if not book:
        return None

    update_data = book_data.model_dump(
        exclude_unset=True
    )

    # If total copies are reduced,
    # don't allow available copies to exceed it.
    new_total = update_data.get(
        "total_copies",
        book.total_copies
    )

    new_available = update_data.get(
        "available_copies",
        book.available_copies
    )

    if new_available > new_total:
        raise ValueError(
            "available_copies cannot be greater than total_copies"
        )

    for field, value in update_data.items():
        setattr(book, field, value)

    db.commit()
    db.refresh(book)

    return book


def delete_book(
    db: Session,
    book_id: int
):
    book = get_book(db, book_id)

    if not book:
        return None

    # Soft delete
    book.is_active = False

    db.commit()
    db.refresh(book)

    return book