from calendar import monthrange
from datetime import date
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

from sqlalchemy import func
from sqlalchemy.orm import Session

from models.loan import Loan, LoanStatus
from models.book import Book


# --------------------------------------------------
# Report directory
# --------------------------------------------------

REPORT_DIR = Path("generated_reports")

REPORT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# --------------------------------------------------
# Generate Monthly Usage Report
# --------------------------------------------------

def generate_monthly_usage_report(
    db: Session,
    year: int,
    month: int
):

    # --------------------------------------------------
    # Validate month
    # --------------------------------------------------

    if month < 1 or month > 12:
        return None, "Month must be between 1 and 12"


    # --------------------------------------------------
    # Calculate month boundaries
    # --------------------------------------------------

    start_date = date(
        year,
        month,
        1
    )

    last_day = monthrange(
        year,
        month
    )[1]

    end_date = date(
        year,
        month,
        last_day
    )


    # --------------------------------------------------
    # Base query
    #
    # Loans issued during selected month
    # --------------------------------------------------

    monthly_loans_query = (
        db.query(Loan)
        .filter(
            Loan.issue_date >= start_date,
            Loan.issue_date <= end_date
        )
    )


    # --------------------------------------------------
    # Total books issued
    # --------------------------------------------------

    total_books_issued = (
        monthly_loans_query
        .count()
    )


    # --------------------------------------------------
    # Returned loans
    # --------------------------------------------------

    total_returned = (
        monthly_loans_query
        .filter(
            Loan.status == LoanStatus.RETURNED
        )
        .count()
    )


    # --------------------------------------------------
    # Currently borrowed
    # --------------------------------------------------

    total_borrowed = (
        monthly_loans_query
        .filter(
            Loan.status == LoanStatus.BORROWED
        )
        .count()
    )


    # --------------------------------------------------
    # Overdue loans
    # --------------------------------------------------

    total_overdue = (
        monthly_loans_query
        .filter(
            Loan.status == LoanStatus.OVERDUE
        )
        .count()
    )


    # --------------------------------------------------
    # Overdue rate
    # --------------------------------------------------

    if total_books_issued > 0:

        overdue_rate = (
            total_overdue
            / total_books_issued
        ) * 100

    else:

        overdue_rate = 0


    # --------------------------------------------------
    # Popular titles
    #
    # Count how many times each book was issued
    # during the selected month.
    # --------------------------------------------------

    popular_titles = (
        db.query(
            Book.title,
            func.count(Loan.id).label("issue_count")
        )
        .join(
            Loan,
            Loan.book_id == Book.id
        )
        .filter(
            Loan.issue_date >= start_date,
            Loan.issue_date <= end_date
        )
        .group_by(
            Book.id,
            Book.title
        )
        .order_by(
            func.count(Loan.id).desc()
        )
        .limit(5)
        .all()
    )


    # --------------------------------------------------
    # PDF path
    # --------------------------------------------------

    file_path = (
        REPORT_DIR
        / f"monthly_usage_{year}_{month:02d}.pdf"
    )


    # --------------------------------------------------
    # Create PDF document
    # --------------------------------------------------

    document = SimpleDocTemplate(
        str(file_path),
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm
    )


    # --------------------------------------------------
    # Styles
    # --------------------------------------------------

    styles = getSampleStyleSheet()


    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=18,
        spaceAfter=6
    )


    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=11,
        spaceAfter=20
    )


    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=13,
        spaceBefore=12,
        spaceAfter=8
    )


    normal_style = ParagraphStyle(
        "NormalText",
        parent=styles["Normal"],
        fontSize=10
    )


    # --------------------------------------------------
    # PDF elements
    # --------------------------------------------------

    elements = []


    # --------------------------------------------------
    # Title
    # --------------------------------------------------

    elements.append(
        Paragraph(
            "LIBRARY MANAGEMENT SYSTEM",
            title_style
        )
    )


    month_name = start_date.strftime("%B %Y")


    elements.append(
        Paragraph(
            f"MONTHLY USAGE REPORT - {month_name}",
            subtitle_style
        )
    )


    # --------------------------------------------------
    # Summary section
    # --------------------------------------------------

    elements.append(
        Paragraph(
            "Monthly Summary",
            heading_style
        )
    )


    summary_data = [
        [
            "Metric",
            "Value"
        ],
        [
            "Books Issued",
            str(total_books_issued)
        ],
        [
            "Returned Loans",
            str(total_returned)
        ],
        [
            "Currently Borrowed",
            str(total_borrowed)
        ],
        [
            "Overdue Loans",
            str(total_overdue)
        ],
        [
            "Overdue Rate",
            f"{overdue_rate:.2f}%"
        ]
    ]


    summary_table = Table(
        summary_data,
        colWidths=[
            100 * mm,
            60 * mm
        ]
    )


    summary_table.setStyle(
        TableStyle([
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),

            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.lightgrey
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),

            (
                "FONTNAME",
                (0, 1),
                (0, -1),
                "Helvetica-Bold"
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),

            (
                "PADDING",
                (0, 0),
                (-1, -1),
                7
            )
        ])
    )


    elements.append(
        summary_table
    )


    # --------------------------------------------------
    # Popular titles
    # --------------------------------------------------

    elements.append(
        Paragraph(
            "Popular Titles",
            heading_style
        )
    )


    popular_data = [
        [
            "Rank",
            "Book Title",
            "Times Issued"
        ]
    ]


    for index, row in enumerate(
        popular_titles,
        start=1
    ):

        popular_data.append([
            str(index),
            row.title,
            str(row.issue_count)
        ])


    if len(popular_data) == 1:

        popular_data.append([
            "-",
            "No books issued during this month",
            "0"
        ])


    popular_table = Table(
        popular_data,
        colWidths=[
            25 * mm,
            100 * mm,
            35 * mm
        ]
    )


    popular_table.setStyle(
        TableStyle([
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),

            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.lightgrey
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),

            (
                "ALIGN",
                (0, 0),
                (0, -1),
                "CENTER"
            ),

            (
                "ALIGN",
                (-1, 0),
                (-1, -1),
                "CENTER"
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),

            (
                "PADDING",
                (0, 0),
                (-1, -1),
                7
            )
        ])
    )


    elements.append(
        popular_table
    )


    # --------------------------------------------------
    # Report note
    # --------------------------------------------------

    elements.append(
        Spacer(1, 20)
    )


    elements.append(
        Paragraph(
            "Note: Overdue rate is calculated using loans issued "
            "during the selected month that currently have "
            "OVERDUE status.",
            normal_style
        )
    )


    # --------------------------------------------------
    # Generate PDF
    # --------------------------------------------------

    document.build(
        elements
    )


    return file_path, None