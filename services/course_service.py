from sqlalchemy.orm import Session

from models.course import Course
from schemas.course import (
    CourseCreate,
    CourseUpdate
)
from utils.query import (
    apply_filter,
    apply_sort,
    paginate_query
)


COURSE_SORT_FIELDS = {
    "id",
    "code",
    "title"
}
COURSE_FILTER_FIELDS = {
    "code",
    "title"
}

def create_course(
    db: Session,
    course_data: CourseCreate
):
    course = Course(
        **course_data.model_dump()
    )

    db.add(course)
    db.commit()
    db.refresh(course)

    return course


def get_courses(
    db: Session,
    page: int = 1,
    limit: int = 10,
    code: str | None = None,
    title: str | None = None,
    is_active: bool | None = None,
    sort: str | None = None
):

    query = db.query(Course)

    query = apply_filter(
        query,
        Course,
        {
            "code": code,
            "title": title
        },
        COURSE_FILTER_FIELDS
    )

    if is_active is not None:
        query = query.filter(
            Course.is_active == is_active
        )
    query = apply_sort(
        query,
        Course,
        sort,
        COURSE_SORT_FIELDS
    )

    return paginate_query(
        query,
        page,
        limit
    )


def get_course(
    db: Session,
    course_id: int
):
    return (
        db.query(Course)
        .filter(Course.id == course_id)
        .first()
    )


def update_course(
    db: Session,
    course_id: int,
    course_data: CourseUpdate
):
    course = get_course(
        db,
        course_id
    )

    if not course:
        return None

    update_data = course_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(
            course,
            field,
            value
        )

    db.commit()
    db.refresh(course)

    return course


def delete_course(
    db: Session,
    course_id: int
):
    course = get_course(
        db,
        course_id
    )

    if not course:
        return None

    course.is_active = False

    db.commit()
    db.refresh(course)

    return course