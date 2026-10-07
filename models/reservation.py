import enum

from datetime import date

  

from sqlalchemy import Date, Enum, ForeignKey

from sqlalchemy.orm import Mapped, mapped_column, relationship

  

from models.base import Base, TimestampMixin

  
  

class ReservationStatus(enum.Enum):

    ACTIVE = "ACTIVE"
    FULFILLED = "FULFILLED"
    CANCELLED = "CANCELLED"


class Reservation(Base, TimestampMixin):

    __tablename__ = "reservations"

    id: Mapped[int] = mapped_column(

    primary_key=True,

    index=True

    )

    

    user_id: Mapped[int] = mapped_column(

    ForeignKey("users.id"),

    nullable=False,

    index=True

    )

    

    book_id: Mapped[int] = mapped_column(

    ForeignKey("books.id"),

    nullable=False,

    index=True

    )

    

    reserved_date: Mapped[date] = mapped_column(

    Date,

    nullable=False

    )

    

    status: Mapped[ReservationStatus] = mapped_column(

    Enum(ReservationStatus),

    nullable=False,

    default=ReservationStatus.ACTIVE

    )

    

    user = relationship(

    "User",

    back_populates="reservations"

    )

    

    book = relationship(

    "Book",

    back_populates="reservations"

    )