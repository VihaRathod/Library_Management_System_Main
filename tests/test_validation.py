import pytest
from pydantic import ValidationError

from schemas.book import BookCreate
from schemas.loan import LoanCreate, LoanUpdate
from schemas.user import UserCreate
from models.loan import LoanStatus

def test_book_rejects_invalid_copies():

    with pytest.raises(ValidationError):

        BookCreate(
            title="Clean Code",
            total_copies=5,
            available_copies=6
        )

def test_book_rejects_empty_title():

    with pytest.raises(ValidationError):

        BookCreate(
            title=""
        )

def test_loan_rejects_invalid_user_id():

    with pytest.raises(ValidationError):

        LoanCreate(
            user_id=0,
            book_id=1
        )

def test_loan_rejects_invalid_book_id():

    with pytest.raises(ValidationError):

        LoanCreate(
            user_id=1,
            book_id=-1
        )

def test_valid_loan():

    loan = LoanCreate(
        user_id=1,
        book_id=2
    )

    assert loan.user_id == 1
    assert loan.book_id == 2

def test_loan_update_allows_returned():

    update = LoanUpdate(
        status=LoanStatus.RETURNED
    )

    assert update.status == LoanStatus.RETURNED
