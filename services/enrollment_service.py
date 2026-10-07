from sqlalchemy.orm import Session

from models.enrollment import Enrollment
from models.user import User, UserRole
from models.course import Course

from schemas.enrollment import EnrollmentCreate


def create_enrollment(
    db: Session,
    enrollment_data: EnrollmentCreate
):

    # Check that the user exists
    user = (
        db.query(User)
        .filter(
            User.id == enrollment_data.user_id
        )
        .first()
    )

    if not user:
        return None, "User not found"

    # Only members can enroll in courses
    if user.role != UserRole.MEMBER:
        return None, "Only members can enroll in courses"

    # User must be active
    if not user.is_active:
        return None, "User is inactive"

    # Check course
    course = (
        db.query(Course)
        .filter(
            Course.id == enrollment_data.course_id
        )
        .first()
    )

    if not course:
        return None, "Course not found"

    if not course.is_active:
        return None, "Course is inactive"

    # Check duplicate enrollment
    existing = (
        db.query(Enrollment)
        .filter(
            Enrollment.user_id == enrollment_data.user_id,
            Enrollment.course_id == enrollment_data.course_id
        )
        .first()
    )

    if existing:
        return None, "User is already enrolled in this course"

    enrollment = Enrollment(
        **enrollment_data.model_dump()
    )

    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)

    return enrollment, None


def get_enrollments(
    db: Session,
    user_id: int | None = None
):

    query = db.query(Enrollment)

    if user_id is not None:
        query = query.filter(
            Enrollment.user_id == user_id
        )

    return query.all()


def get_enrollment(
    db: Session,
    enrollment_id: int
):

    return (
        db.query(Enrollment)
        .filter(
            Enrollment.id == enrollment_id
        )
        .first()
    )


def delete_enrollment(
    db: Session,
    enrollment_id: int
):

    enrollment = get_enrollment(
        db,
        enrollment_id
    )

    if not enrollment:
        return None

    db.delete(enrollment)
    db.commit()

    return enrollment