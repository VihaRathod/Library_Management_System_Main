from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from fastapi.responses import FileResponse

from sqlalchemy.orm import Session

from database.connection import get_db

from dependencies.auth import require_role

from models.user import User, UserRole

from services.loan_service import get_loan
from services.receipt_service import (
    generate_checkout_receipt
)

from services.email_service import (
    send_receipt_email
)


router = APIRouter(
    prefix="/loans",
    tags=["Receipts"]
)


@router.get(
    "/{loan_id}/receipt"
)
def generate_receipt(
    loan_id: int,
    db: Session = Depends(get_db),

    current_user: User = Depends(
        require_role(UserRole.LIBRARIAN)
    )
):

    file_path, error = generate_checkout_receipt(
        db,
        loan_id
    )

    if error:
        raise HTTPException(
            status_code=404,
            detail=error
        )

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=f"checkout_receipt_{loan_id}.pdf"
    )


@router.post(
    "/{loan_id}/receipt/email"
)
def email_receipt(
    loan_id: int,
    db: Session = Depends(get_db),

    current_user: User = Depends(
        require_role(UserRole.LIBRARIAN)
    )
):

    # -----------------------------------------
    # Generate receipt
    # -----------------------------------------

    file_path, error = generate_checkout_receipt(
        db,
        loan_id
    )

    if error:
        raise HTTPException(
            status_code=404,
            detail=error
        )

    # -----------------------------------------
    # Get loan
    # -----------------------------------------

    loan = get_loan(
        db,
        loan_id
    )

    if not loan:
        raise HTTPException(
            status_code=404,
            detail="Loan not found"
        )

    # -----------------------------------------
    # Get member
    # -----------------------------------------

    user = loan.user
    book = loan.book

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User associated with loan not found"
        )

    if not book:
        raise HTTPException(
            status_code=404,
            detail="Book associated with loan not found"
        )

    # -----------------------------------------
    # Send email
    # -----------------------------------------

    email_sent = send_receipt_email(
        recipient_email=user.email,
        book_title=book.title,
        issue_date=loan.issue_date,
        due_date=loan.due_date,
        receipt_path=file_path
    )

    if not email_sent:

        raise HTTPException(
            status_code=500,
            detail="Failed to send receipt email"
        )

    return {
        "message": "Receipt emailed successfully",
        "recipient": user.email,
        "loan_id": loan.id
    }