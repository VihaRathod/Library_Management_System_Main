from sqlalchemy.orm import Session

from models.author import Author
from schemas.author import (
    AuthorCreate,
    AuthorUpdate
)

from sqlalchemy.orm import Session

from models.author import Author

from schemas.author import (
    AuthorCreate,
    AuthorUpdate
)

from utils.query import (
    apply_filter,
    apply_sort,
    paginate_query
)


AUTHOR_SORT_FIELDS = {
    "id",
    "name"
}
AUTHOR_FILTER_FIELDS = {
    "name"
}
def create_author(
    db: Session,
    author_data: AuthorCreate
):
    author = Author(
        **author_data.model_dump()
    )

    db.add(author)
    db.commit()
    db.refresh(author)

    return author



def get_authors(
    db: Session,
    page: int = 1,
    limit: int = 10,
    name: str | None = None,
    sort: str | None = None
):

    query = db.query(Author)

    query = apply_filter(
        query,
        Author,
        {
            "name": name
        },
        AUTHOR_FILTER_FIELDS
    )

    query = apply_sort(
        query,
        Author,
        sort,
        AUTHOR_SORT_FIELDS
    )

    return paginate_query(query, page, limit)

def get_author(
    db: Session,
    author_id: int
):
    return (
        db.query(Author)
        .filter(Author.id == author_id)
        .first()
    )


def update_author(
    db: Session,
    author_id: int,
    author_data: AuthorUpdate
):
    author = get_author(
        db,
        author_id
    )

    if not author:
        return None

    update_data = author_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(
            author,
            field,
            value
        )

    db.commit()
    db.refresh(author)

    return author


def delete_author(
    db: Session,
    author_id: int
):
    author = get_author(
        db,
        author_id
    )

    if not author:
        return None

    db.delete(author)
    db.commit()

    return author