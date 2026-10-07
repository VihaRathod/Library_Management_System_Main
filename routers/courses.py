from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from schemas.pagination import PageResponse
from database.connection import get_db

from schemas.course import (
    CourseCreate,
    CourseUpdate,
    CourseResponse
)

from services.course_service import (
    create_course,
    get_courses,
    get_course,
    update_course,
    delete_course
)
from dependencies.auth import get_current_user,require_role
from models.user import User, UserRole

router = APIRouter(
    prefix="/courses",
    tags=["Courses"]
)


@router.post(
    "/",
    response_model=CourseResponse,
    status_code=status.HTTP_201_CREATED
)
def create(
    course_data: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.LIBRARIAN)
    )
):
    return create_course(
        db,
        course_data
    )


@router.get(
    "/",
    response_model=PageResponse[CourseResponse]
)
def get_all(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),

    code: str | None = Query(None),
    title: str | None = Query(None),
    sort: str | None = Query(None),

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    return get_courses(
        db=db,
        page=page,
        limit=limit,
        code=code,
        title=title,
        sort=sort
    )


@router.get(
    "/{course_id}",
    response_model=CourseResponse
)
def get_one(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):
    course = get_course(
        db,
        course_id
    )

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    return course


@router.put(
    "/{course_id}",
    response_model=CourseResponse
)
def update(
    course_id: int,
    course_data: CourseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.LIBRARIAN)
    )
):
    course = update_course(
        db,
        course_id,
        course_data
    )

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    return course


@router.delete(
    "/{course_id}"
)
def delete(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.LIBRARIAN)
    )
):
    course = delete_course(
        db,
        course_id
    )

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    return {
        "message": "Course deleted successfully"
    }