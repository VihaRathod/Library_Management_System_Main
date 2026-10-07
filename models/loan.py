import enum
from datetime import date

from sqlalchemy import Date, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin


class LoanStatus(enum.Enum):
    BORROWED = "BORROWED"
    RETURNED = "RETURNED"
    OVERDUE = "OVERDUE"


class Loan(Base, TimestampMixin):

    __tablename__ = "loans"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    book_id: Mapped[int] = mapped_column(
        ForeignKey("books.id"),
        nullable=False
    )

    issue_date: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    due_date: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    return_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    status: Mapped[LoanStatus] = mapped_column(
        Enum(LoanStatus),
        nullable=False,
        default=LoanStatus.BORROWED
    )

    receipt_path: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    user = relationship(
        "User",
        back_populates="loans"
    )

    book = relationship(
        "Book",
        back_populates="loans"
    )