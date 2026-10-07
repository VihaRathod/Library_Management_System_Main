from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin


class Author(Base, TimestampMixin):

    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True
    )

    books = relationship(
        "Book",
        secondary="book_authors",
        back_populates="authors"
    )