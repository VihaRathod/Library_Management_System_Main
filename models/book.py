import enum

from sqlalchemy import Boolean, Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin


class BookType(enum.Enum):
    PHYSICAL = "PHYSICAL"
    DIGITAL = "DIGITAL"


class Book(Base, TimestampMixin):

    __tablename__ = "books"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True
    )

    isbn: Mapped[str | None] = mapped_column(
        String(20),
        unique=True,
        nullable=True
    )

    book_type: Mapped[BookType] = mapped_column(
        Enum(BookType),
        nullable=False,
        default=BookType.PHYSICAL
    )

    total_copies: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1
    )

    available_copies: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1
    )

    file_path: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    published_year: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )

    authors = relationship(
        "Author",
        secondary="book_authors",
        back_populates="books"
    )

    loans = relationship(
        "Loan",
        back_populates="book"
    )

    courses = relationship(
        "Course",
        secondary="course_books",
        back_populates="books"
    )

    reservations = relationship(
        "Reservation",
        back_populates="book"
    )