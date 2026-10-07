from datetime import date, timedelta

import pytest
from pydantic import ValidationError

from models.loan import Loan, LoanStatus
from schemas.loan import LoanUpdate
from services.loan_service import is_loan_overdue


def test_loan_is_overdue():

    loan = Loan(
        status=LoanStatus.BORROWED,
        due_date=date.today() - timedelta(days=2)
    )

    assert is_loan_overdue(loan) is True


def test_loan_is_not_overdue_before_due_date():

    loan = Loan(
        status=LoanStatus.BORROWED,
        due_date=date.today() + timedelta(days=2)
    )

    assert is_loan_overdue(loan) is False


def test_loan_is_not_overdue_on_due_date():

    loan = Loan(
        status=LoanStatus.BORROWED,
        due_date=date.today()
    )

    assert is_loan_overdue(loan) is False


def test_returned_loan_is_not_overdue():

    loan = Loan(
        status=LoanStatus.RETURNED,
        due_date=date.today() - timedelta(days=5)
    )

    assert is_loan_overdue(loan) is False


def test_loan_due_date_is_14_days_after_issue_date():

    issue_date = date.today()

    due_date = issue_date + timedelta(days=14)

    assert due_date == date.today() + timedelta(days=14)


def test_loan_update_allows_returned():

    data = LoanUpdate(
        status=LoanStatus.RETURNED
    )

    assert data.status == LoanStatus.RETURNED

