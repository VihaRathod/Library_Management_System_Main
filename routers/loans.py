from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.connection import get_db
from fastapi import Query
from models.loan import LoanStatus
from schemas.pagination import PageResponse
from schemas.loan import (
    LoanCreate,
    LoanUpdate,
    LoanResponse
)

from services.loan_service import (
    create_loan,
    get_loans,
    get_loan,
    update_loan
)


router = APIRouter(
    prefix="/loans",
    tags=["Loans"]
)
from dependencies.auth import get_current_user,require_role
from models.user import User, UserRole

@router.post(
    "/",
    response_model=LoanResponse,
    status_code=status.HTTP_201_CREATED
)
def create(
    loan_data: LoanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.LIBRARIAN)
    )
):

    loan, error = create_loan(
        db,
        loan_data
    )

    if error:
        raise HTTPException(
            status_code=400,
            detail=error
        )

    return loan


@router.get(
    "/",
    response_model=PageResponse[LoanResponse]
)
def get_all(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),

    status: LoanStatus | None = Query(None),
    user_id: int | None = Query(None, gt=0),
    book_id: int | None = Query(None, gt=0),

    sort: str | None = Query(None),

    db: Session = Depends(get_db),

    current_user: User = Depends(
        require_role(UserRole.LIBRARIAN)
    )
):

    return get_loans(
        db=db,
        page=page,
        limit=limit,
        status=status,
        user_id=user_id,
        book_id=book_id,
        sort=sort
    )


@router.get(
    "/{loan_id}",
    response_model=LoanResponse
)
def get_one(
    loan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.LIBRARIAN)
    )
):

    loan = get_loan(
        db,
        loan_id
    )

    if not loan:
        raise HTTPException(
            status_code=404,
            detail="Loan not found"
        )

    return loan


@router.put(
    "/{loan_id}",
    response_model=LoanResponse
)
def update(
    loan_id: int,
    loan_data: LoanUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.LIBRARIAN)
    )
):

    loan, error = update_loan(
        db,
        loan_id,
        loan_data
    )

    if error:
        raise HTTPException(
            status_code=400,
            detail=error
        )

    return loan