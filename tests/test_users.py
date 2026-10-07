from models.user import UserRole
from schemas.user import UserCreate


def test_user_email_is_valid():

    user = UserCreate(
        email="member@example.com",
        password="password123",
        name="Viha"
    )

    assert str(user.email) == "member@example.com"


def test_user_password_minimum_length():

    try:
        UserCreate(
            email="member@example.com",
            password="123",
            name="Viha"
        )

        assert False, "Validation should have failed"

    except ValueError:
        assert True


def test_user_name_minimum_length():

    try:
        UserCreate(
            email="member@example.com",
            password="password123",
            name="A"
        )

        assert False, "Validation should have failed"

    except ValueError:
        assert True


def test_user_phone_is_optional():

    user = UserCreate(
        email="member@example.com",
        password="password123",
        name="Viha"
    )

    assert user.phone is None