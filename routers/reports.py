from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query
)

from fastapi.responses import FileResponse

from sqlalchemy.orm import Session

from database.connection import get_db

from dependencies.auth import require_role

from models.user import User, UserRole

from services.report_service import (
    generate_monthly_usage_report
)


router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)


@router.get(
    "/monthly-usage"
)
def monthly_usage_report(
    year: int = Query(
        ...,
        ge=2000,
        le=2026
    ),

    month: int = Query(
        ...,
        ge=1,
        le=12
    ),

    db: Session = Depends(get_db),

    current_user: User = Depends(
        require_role(UserRole.LIBRARIAN)
    )
):

    file_path, error = generate_monthly_usage_report(
        db=db,
        year=year,
        month=month
    )


    if error:

        raise HTTPException(
            status_code=400,
            detail=error
        )


    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=(
            f"monthly_usage_report_"
            f"{year}_{month:02d}.pdf"
        )
    )