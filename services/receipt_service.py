from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from sqlalchemy.orm import Session

from models.loan import Loan


# -----------------------------------------
# Receipt directory
# -----------------------------------------

RECEIPT_DIR = Path("generated_receipts")

RECEIPT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def generate_checkout_receipt(
    db: Session,
    loan_id: int
):

    # -----------------------------------------
    # Get loan
    # -----------------------------------------

    loan = (
        db.query(Loan)
        .filter(
            Loan.id == loan_id
        )
        .first()
    )

    if not loan:
        return None, "Loan not found"


    # -----------------------------------------
    # Get related data
    # -----------------------------------------

    user = loan.user
    book = loan.book

    if not user:
        return None, "User associated with loan not found"

    if not book:
        return None, "Book associated with loan not found"


    # -----------------------------------------
    # PDF path
    # -----------------------------------------

    file_path = RECEIPT_DIR / f"receipt_{loan.id}.pdf"


    # -----------------------------------------
    # PDF document
    # -----------------------------------------

    document = SimpleDocTemplate(
        str(file_path),
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm
    )


    styles = getSampleStyleSheet()


    title_style = ParagraphStyle(
        "ReceiptTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=18,
        spaceAfter=6
    )


    subtitle_style = ParagraphStyle(
        "ReceiptSubtitle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=11,
        spaceAfter=20
    )


    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=12,
        spaceBefore=10,
        spaceAfter=8
    )


    normal_style = ParagraphStyle(
        "NormalText",
        parent=styles["Normal"],
        fontSize=10
    )


    # -----------------------------------------
    # Content
    # -----------------------------------------

    elements = []


    elements.append(
        Paragraph(
            "LIBRARY MANAGEMENT SYSTEM",
            title_style
        )
    )


    elements.append(
        Paragraph(
            "CHECKOUT RECEIPT",
            subtitle_style
        )
    )


    # -----------------------------------------
    # Receipt information
    # -----------------------------------------

    elements.append(
        Paragraph(
            "Receipt Information",
            heading_style
        )
    )


    receipt_data = [
        ["Loan ID", str(loan.id)],
        ["Issue Date", loan.issue_date.strftime("%d-%m-%Y")],
        ["Due Date", loan.due_date.strftime("%d-%m-%Y")],
        ["Status", loan.status.value],
    ]


    receipt_table = Table(
        receipt_data,
        colWidths=[55 * mm, 105 * mm]
    )


    receipt_table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("PADDING", (0, 0), (-1, -1), 7),
        ])
    )


    elements.append(receipt_table)


    # -----------------------------------------
    # Member information
    # -----------------------------------------

    elements.append(
        Paragraph(
            "Member Information",
            heading_style
        )
    )


    member_data = [
        ["User ID", str(user.id)],
        ["Email", user.email],
    ]


    member_table = Table(
        member_data,
        colWidths=[55 * mm, 105 * mm]
    )


    member_table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("PADDING", (0, 0), (-1, -1), 7),
        ])
    )


    elements.append(member_table)


    # -----------------------------------------
    # Book information
    # -----------------------------------------

    elements.append(
        Paragraph(
            "Book Information",
            heading_style
        )
    )


    book_data = [
        ["Book ID", str(book.id)],
        ["Title", book.title],
        ["ISBN", book.isbn or "N/A"],
        ["Book Type", book.book_type.value],
    ]


    book_table = Table(
        book_data,
        colWidths=[55 * mm, 105 * mm]
    )


    book_table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("PADDING", (0, 0), (-1, -1), 7),
        ])
    )


    elements.append(book_table)


    # -----------------------------------------
    # Footer message
    # -----------------------------------------

    elements.append(
        Spacer(1, 25)
    )


    elements.append(
        Paragraph(
            "Please return the book before the due date.",
            normal_style
        )
    )


    elements.append(
        Paragraph(
            "Thank you for using the Library Management System.",
            normal_style
        )
    )


    # -----------------------------------------
    # Generate PDF
    # -----------------------------------------

    document.build(elements)


    # -----------------------------------------
    # Save path in database
    # -----------------------------------------

    loan.receipt_path = str(file_path)

    db.commit()
    db.refresh(loan)


    return file_path, None