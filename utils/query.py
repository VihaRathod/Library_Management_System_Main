import math

from fastapi import HTTPException, status
from sqlalchemy.orm import Query


from fastapi import HTTPException, status
from sqlalchemy.orm import Query
import math


def apply_filter(
    query: Query,
    model,
    filters: dict[str, str | None],
    allowed_fields: set[str]
):
    for field, value in filters.items():

        # Ignore filters that were not provided
        if value is None or value == "null":
            continue

        # Make sure the field is allowed
        if field not in allowed_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Filtering by '{field}' is not allowed"
            )

        try:
            column = getattr(model, field)

            query = query.filter(
                column.ilike(f"%{value}%")
            )

        except AttributeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid filter field: '{field}'"
            )

    return query



def paginate_query(
    query: Query,
    page: int,
    limit: int
):

    total_record = query.count()

    total_pages = (
        math.ceil(total_record / limit)
        if total_record
        else 0
    )

    offset = (page - 1) * limit

    content = (
        query
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "page_number": page,
        "page_size": limit,
        "total_pages": total_pages,
        "total_record": total_record,
        "content": content
    }


def apply_sort(
    query: Query,
    model,
    sort: str | None,
    allowed_fields: set[str]
):

    if not sort:
        return query

    # Example:
    # sort=title
    # sort=desc:title
    # sort=title,desc:published_year

    for field in sort.split(","):

        is_desc = field.startswith("desc:")

        field_name = field.replace(
            "desc:",
            "",
            1
        )

        if field_name not in allowed_fields:
            raise ValueError(
                f"Sorting by '{field_name}' is not allowed"
            )

        column = getattr(
            model,
            field_name
        )

        if is_desc:
            query = query.order_by(
                column.desc()
            )
        else:
            query = query.order_by(
                column.asc()
            )

    return query