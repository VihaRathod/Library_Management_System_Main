from database.connection import SessionLocal

from services.loan_service import get_overdue_loans
from services.email_service import send_overdue_reminder


def overdue_reminder_job():

    print("Starting overdue reminder job...")

    db = SessionLocal()

    try:

        overdue_loans = get_overdue_loans(db)

        print(
            f"Found {len(overdue_loans)} overdue loan(s)"
        )

        for loan in overdue_loans:

            user = loan.user
            book = loan.book

            if not user or not book:
                continue

            send_overdue_reminder(
                recipient_email=user.email,
                book_title=book.title,
                due_date=loan.due_date
            )

        print("Overdue reminder job completed.")

    except Exception as e:

        print(
            f"Overdue reminder job failed: {e}"
        )

    finally:

        db.close()