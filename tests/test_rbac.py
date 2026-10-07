import pytest
from fastapi import HTTPException

from dependencies.auth import require_role
from models.user import User, UserRole


def test_librarian_can_access_librarian_route():

    librarian = User(
        id=1,
        email="librarian@example.com",
        role=UserRole.LIBRARIAN,
        is_active=True
    )

    checker = require_role(UserRole.LIBRARIAN)

    result = checker(librarian)

    assert result == librarian


def test_member_cannot_access_librarian_route():

    member = User(
        id=2,
        email="member@example.com",
        role=UserRole.MEMBER,
        is_active=True
    )

    checker = require_role(UserRole.LIBRARIAN)

    with pytest.raises(HTTPException) as error:

        checker(member)

    assert error.value.status_code == 403
    assert error.value.detail == "Not enough permissions"


def test_member_can_access_member_route():

    member = User(
        id=2,
        email="member@example.com",
        role=UserRole.MEMBER,
        is_active=True
    )

    checker = require_role(UserRole.MEMBER)

    result = checker(member)

    assert result == member

def test_multiple_roles_are_allowed():

    member = User(
        id=2,
        email="member@example.com",
        role=UserRole.MEMBER,
        is_active=True
    )

    checker = require_role(
        UserRole.LIBRARIAN,
        UserRole.MEMBER
    )

    result = checker(member)

    assert result == member