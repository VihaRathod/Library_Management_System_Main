from models.book import BookType
from schemas.book import BookCreate, BookUpdate


def test_physical_book_default_type():

    book = BookCreate(
        title="Clean Code"
    )

    assert book.book_type == BookType.PHYSICAL


def test_digital_book():

    book = BookCreate(
        title="Python Crash Course",
        book_type=BookType.DIGITAL
    )

    assert book.book_type == BookType.DIGITAL


def test_available_copies_cannot_exceed_total_copies():

    try:
        BookCreate(
            title="Clean Code",
            total_copies=5,
            available_copies=6
        )

        assert False, "Validation should have failed"

    except ValueError:
        assert True


def test_valid_book_copies():

    book = BookCreate(
        title="Clean Code",
        total_copies=5,
        available_copies=3
    )

    assert book.total_copies == 5
    assert book.available_copies == 3


def test_book_title_cannot_be_empty():

    try:
        BookCreate(
            title=""
        )

        assert False, "Validation should have failed"

    except ValueError:
        assert True