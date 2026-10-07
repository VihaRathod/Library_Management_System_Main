import smtplib

from pathlib import Path

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

from config.settings import settings


# ============================================================
# Generic Email Sender
# ============================================================

def send_email(
    recipient_email: str,
    subject: str,
    body: str,
    attachment_path: Path | None = None
):

    message = MIMEMultipart()

    message["From"] = settings.smtp_from_email
    message["To"] = recipient_email
    message["Subject"] = subject

    # --------------------------------------------------------
    # Email body
    # --------------------------------------------------------

    message.attach(
        MIMEText(
            body,
            "plain"
        )
    )

    # --------------------------------------------------------
    # Attachment
    # --------------------------------------------------------

    if attachment_path:

        with open(
            attachment_path,
            "rb"
        ) as file:

            attachment = MIMEApplication(
                file.read(),
                _subtype="pdf"
            )

        attachment.add_header(
            "Content-Disposition",
            "attachment",
            filename=attachment_path.name
        )

        message.attach(
            attachment
        )

    # --------------------------------------------------------
    # Send email
    # --------------------------------------------------------

    try:

        with smtplib.SMTP(
            settings.smtp_host,
            settings.smtp_port
        ) as server:

            # MailHog does not require authentication.
            # For a real SMTP provider, credentials can be used.

            if (
                settings.smtp_username
                and settings.smtp_password
            ):

                server.starttls()

                server.login(
                    settings.smtp_username,
                    settings.smtp_password
                )

            server.sendmail(
                settings.smtp_from_email,
                recipient_email,
                message.as_string()
            )

        print(
            f"Email sent to {recipient_email}"
        )

        return True

    except Exception as e:

        print(
            f"Failed to send email: {e}"
        )

        return False


# ============================================================
# Overdue Reminder Email
# ============================================================

def send_overdue_reminder(
    recipient_email: str,
    book_title: str,
    due_date
):

    subject = (
        f"Library Book Overdue - "
        f"{book_title}"
    )

    body = f"""
Hello,

This is a reminder from the Library Management System.

The following book is overdue:

Book: {book_title}
Due Date: {due_date}

Please return the book as soon as possible.

Thank you,
Library Management System
"""

    return send_email(
        recipient_email=recipient_email,
        subject=subject,
        body=body
    )


# ============================================================
# Checkout Receipt Email
# ============================================================

def send_receipt_email(
    recipient_email: str,
    book_title: str,
    issue_date,
    due_date,
    receipt_path: Path
):

    subject = (
        f"Library Checkout Receipt - "
        f"{book_title}"
    )

    body = f"""
Hello,

Your book checkout has been successfully recorded.

Book: {book_title}
Issue Date: {issue_date}
Due Date: {due_date}

Your checkout receipt is attached to this email.

Please return the book before the due date.

Thank you,
Library Management System
"""

    return send_email(
        recipient_email=recipient_email,
        subject=subject,
        body=body,
        attachment_path=receipt_path
    )