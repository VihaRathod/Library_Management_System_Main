from datetime import date, timedelta

from sqlalchemy.orm import Session

from models.book import Book, BookType
from models.user import User, UserRole
from models.loan import Loan, LoanStatus

from schemas.loan import LoanCreate, LoanUpdate
from config.settings import settings
from utils.query import (
    apply_sort,
    paginate_query
)


LOAN_SORT_FIELDS = {
    "id",
    "issue_date",
    "due_date",
    "return_date"
}


def create_loan(
    db: Session,
    loan_data: LoanCreate
):

    # -----------------------------------------
    # Check user
    # -----------------------------------------

    user = (
        db.query(User)
        .filter(
            User.id == loan_data.user_id
        )
        .first()
    )

    if not user:
        return None, "User not found"

    # Only MEMBER can borrow books
    if user.role != UserRole.MEMBER:
        return None, "Only members can borrow books"

    # User must be active
    if not user.is_active:
        return None, "User is inactive"

    # -----------------------------------------
    # Check book
    # -----------------------------------------

    book = (
        db.query(Book)
        .filter(
            Book.id == loan_data.book_id
        )
        .first()
    )

    if not book:
        return None, "Book not found"

    if not book.is_active:
        return None, "Book is inactive"

    # -----------------------------------------
    # Check existing active loan
    # -----------------------------------------

    existing_loan = (
        db.query(Loan)
        .filter(
            Loan.user_id == loan_data.user_id,
            Loan.book_id == loan_data.book_id,
            Loan.status.in_([
                LoanStatus.BORROWED,
                LoanStatus.OVERDUE
            ])
        )
        .first()
    )

    if existing_loan:
        return None, "User already has this book borrowed"

    # -----------------------------------------
    # Physical book availability
    # -----------------------------------------

    if book.book_type == BookType.PHYSICAL:

        if book.available_copies <= 0:
            return None, "No copies available"

        book.available_copies -= 1

    # -----------------------------------------
    # Calculate loan dates
    # -----------------------------------------

    issue_date = date.today()

    due_date = issue_date + timedelta(
        days=settings.loan_duration_days
    )

    # -----------------------------------------
    # Create loan
    # -----------------------------------------

    loan = Loan(
        user_id=loan_data.user_id,
        book_id=loan_data.book_id,
        issue_date=issue_date,
        due_date=due_date,
        status=LoanStatus.BORROWED
    )

    db.add(loan)
    db.commit()
    db.refresh(loan)

    return loan, None



def get_loans(
    db: Session,
    page: int = 1,
    limit: int = 10,
    status: LoanStatus | None = None,
    user_id: int | None = None,
    book_id: int | None = None,
    sort: str | None = None
):

    query = db.query(Loan)

    if status is not None:
        query = query.filter(
            Loan.status == status
        )

    if user_id is not None:
        query = query.filter(
            Loan.user_id == user_id
        )

    if book_id is not None:
        query = query.filter(
            Loan.book_id == book_id
        )

    query = apply_sort(
        query,
        Loan,
        sort,
        LOAN_SORT_FIELDS
    )

    return paginate_query(
        query,
        page,
        limit
    )


def get_loan(
    db: Session,
    loan_id: int
):

    return (
        db.query(Loan)
        .filter(
            Loan.id == loan_id
        )
        .first()
    )


def update_loan(
    db: Session,
    loan_id: int,
    loan_data: LoanUpdate
):

    loan = get_loan(
        db,
        loan_id
    )

    if not loan:
        return None, "Loan not found"

    update_data = loan_data.model_dump(
        exclude_unset=True
    )

    # -----------------------------------------
    # Returning a book
    # -----------------------------------------

    if (
        update_data.get("status") == LoanStatus.RETURNED
        and loan.status != LoanStatus.RETURNED
    ):

        book = (
            db.query(Book)
            .filter(
                Book.id == loan.book_id
            )
            .first()
        )

        if (
            book
            and book.book_type == BookType.PHYSICAL
        ):
            book.available_copies += 1

        if "return_date" not in update_data:
            update_data["return_date"] = date.today()

    for field, value in update_data.items():
        setattr(
            loan,
            field,
            value
        )

    db.commit()
    db.refresh(loan)

    return loan, None


def is_loan_overdue(loan: Loan) -> bool:

    return (
        loan.status == LoanStatus.BORROWED
        and loan.due_date < date.today()
    )

def mark_overdue_loans(db: Session):

    today = date.today()

    overdue_loans = (
        db.query(Loan)
        .filter(
            Loan.status == LoanStatus.BORROWED,
            Loan.due_date < today
        )
        .all()
    )

    for loan in overdue_loans:
        loan.status = LoanStatus.OVERDUE

    db.commit()

    return overdue_loans

def get_overdue_loans(db: Session):

    today = date.today()

    overdue_loans = (
        db.query(Loan)
        .filter(
            Loan.status.in_([
                LoanStatus.BORROWED,
                LoanStatus.OVERDUE
            ]),
            Loan.due_date < today
        )
        .all()
    )

    for loan in overdue_loans:

        if loan.status == LoanStatus.BORROWED:
            loan.status = LoanStatus.OVERDUE

    db.commit()

    return overdue_loans