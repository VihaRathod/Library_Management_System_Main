from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class CourseBook(Base):

    __tablename__ = "course_books"

    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id"),
        primary_key=True
    )

    book_id: Mapped[int] = mapped_column(
        ForeignKey("books.id"),
        primary_key=True
    )