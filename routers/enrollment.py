from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.connection import get_db

from dependencies.auth import get_current_user

from models.user import User, UserRole

from schemas.enrollment import (
    EnrollmentCreate,
    EnrollmentResponse
)

from services.enrollment_service import (
    create_enrollment,
    get_enrollments,
    get_enrollment,
    delete_enrollment
)


router = APIRouter(
    prefix="/enrollments",
    tags=["Enrollments"]
)


# --------------------------------------------------
# CREATE ENROLLMENT
# --------------------------------------------------

@router.post(
    "/",
    response_model=EnrollmentResponse,
    status_code=status.HTTP_201_CREATED
)
def create(
    enrollment_data: EnrollmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # MEMBER
    if current_user.role == UserRole.MEMBER:

        # Ignore the user_id sent by client.
        # Always use authenticated user's ID.
        enrollment_data.user_id = current_user.id

    # LIBRARIAN can create for any user.
    enrollment, error = create_enrollment(
        db,
        enrollment_data
    )

    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    return enrollment


# --------------------------------------------------
# GET ALL ENROLLMENTS
# --------------------------------------------------

@router.get(
    "/",
    response_model=list[EnrollmentResponse]
)
def get_all(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # LIBRARIAN
    if current_user.role == UserRole.LIBRARIAN:
        return get_enrollments(db)

    # MEMBER
    return get_enrollments(
        db,
        user_id=current_user.id
    )


# --------------------------------------------------
# GET ONE ENROLLMENT
# --------------------------------------------------

@router.get(
    "/{enrollment_id}",
    response_model=EnrollmentResponse
)
def get_one(
    enrollment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    enrollment = get_enrollment(
        db,
        enrollment_id
    )

    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found"
        )

    # LIBRARIAN
    if current_user.role == UserRole.LIBRARIAN:
        return enrollment

    # MEMBER ownership check
    if enrollment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    return enrollment


# --------------------------------------------------
# DELETE ENROLLMENT
# --------------------------------------------------

@router.delete(
    "/{enrollment_id}"
)
def delete(
    enrollment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    enrollment = get_enrollment(
        db,
        enrollment_id
    )

    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found"
        )

    # LIBRARIAN
    if current_user.role == UserRole.LIBRARIAN:

        delete_enrollment(
            db,
            enrollment_id
        )

        return {
            "message": "Enrollment deleted successfully"
        }

    # MEMBER ownership check
    if enrollment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    delete_enrollment(
        db,
        enrollment_id
    )

    return {
        "message": "Enrollment deleted successfully"
    }