from __future__ import annotations

import csv
import os
from datetime import date
from typing import List

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from .db import Database
from .models import Expense, Payment
from .utils import format_inr


def export_month_csv(db: Database, year: int, month: int, export_path: str) -> str:
    os.makedirs(os.path.dirname(export_path), exist_ok=True)
    payments = db.list_payments_in_month(year, month)
    expenses = db.list_expenses_in_month(year, month)
    with open(export_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([f"Monthly Report {year}-{month:02d}"])
        writer.writerow([])
        writer.writerow(["Receipts"])
        writer.writerow(["Payment ID", "Flat ID", "Date", "For Period", "Amount", "Note"])
        for p in payments:
            writer.writerow([p.id, p.flat_id, p.paid_on.isoformat(), f"{p.period_year}-{p.period_month:02d}", p.amount, p.note])
        writer.writerow([])
        writer.writerow(["Expenses"])
        writer.writerow(["Expense ID", "Category", "Date", "Amount", "Description", "Paid By Flat ID"])
        for e in expenses:
            writer.writerow([e.id, e.category, e.spent_on.isoformat(), e.amount, e.description, e.paid_by_flat_id or "-"])
    return export_path


def export_year_csv(db: Database, year: int, export_path: str) -> str:
    os.makedirs(os.path.dirname(export_path), exist_ok=True)
    payments = db.list_payments_in_year(year)
    expenses = db.list_expenses_in_year(year)
    with open(export_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([f"Yearly Report {year}"])
        writer.writerow([])
        writer.writerow(["Receipts"])
        writer.writerow(["Payment ID", "Flat ID", "Date", "For Period", "Amount", "Note"])
        for p in payments:
            writer.writerow([p.id, p.flat_id, p.paid_on.isoformat(), f"{p.period_year}-{p.period_month:02d}", p.amount, p.note])
        writer.writerow([])
        writer.writerow(["Expenses"])
        writer.writerow(["Expense ID", "Category", "Date", "Amount", "Description", "Paid By Flat ID"])
        for e in expenses:
            writer.writerow([e.id, e.category, e.spent_on.isoformat(), e.amount, e.description, e.paid_by_flat_id or "-"])
    return export_path


def _draw_header(c: canvas.Canvas, title: str) -> None:
    c.setFont("Helvetica-Bold", 14)
    c.drawString(20 * mm, 285 * mm, title)
    c.setFont("Helvetica", 9)
    c.drawString(20 * mm, 280 * mm, f"Generated on: {date.today().isoformat()}")


def export_month_pdf(db: Database, year: int, month: int, export_path: str) -> str:
    os.makedirs(os.path.dirname(export_path), exist_ok=True)
    payments = db.list_payments_in_month(year, month)
    expenses = db.list_expenses_in_month(year, month)
    total_receipts = sum(p.amount for p in payments)
    total_expenses = sum(e.amount for e in expenses)

    c = canvas.Canvas(export_path, pagesize=A4)
    _draw_header(c, f"Monthly Report {year}-{month:02d}")

    y = 270
    c.setFont("Helvetica-Bold", 11)
    c.drawString(20 * mm, y * mm, "Receipts")
    y -= 7
    c.setFont("Helvetica", 9)
    for p in payments:
        line = f"ID {p.id} | Flat {p.flat_id} | {p.paid_on.isoformat()} | For {p.period_year}-{p.period_month:02d} | {format_inr(p.amount)}"
        c.drawString(20 * mm, y * mm, line)
        y -= 5
        if y < 25:
            c.showPage()
            _draw_header(c, f"Monthly Report {year}-{month:02d} (cont.)")
            y = 270
    c.setFont("Helvetica-Bold", 10)
    c.drawString(20 * mm, y * mm, f"Total Receipts: {format_inr(total_receipts)}")
    y -= 10

    c.setFont("Helvetica-Bold", 11)
    c.drawString(20 * mm, y * mm, "Expenses")
    y -= 7
    c.setFont("Helvetica", 9)
    for e in expenses:
        payer = f"Flat {e.paid_by_flat_id}" if e.paid_by_flat_id else "Society"
        line = f"ID {e.id} | {e.category} | {e.spent_on.isoformat()} | {format_inr(e.amount)} | {payer} | {e.description}"
        c.drawString(20 * mm, y * mm, line)
        y -= 5
        if y < 25:
            c.showPage()
            _draw_header(c, f"Monthly Report {year}-{month:02d} (cont.)")
            y = 270
    c.setFont("Helvetica-Bold", 10)
    c.drawString(20 * mm, y * mm, f"Total Expenses: {format_inr(total_expenses)}")

    c.showPage()
    c.save()
    return export_path


def export_year_pdf(db: Database, year: int, export_path: str) -> str:
    os.makedirs(os.path.dirname(export_path), exist_ok=True)
    payments = db.list_payments_in_year(year)
    expenses = db.list_expenses_in_year(year)
    total_receipts = sum(p.amount for p in payments)
    total_expenses = sum(e.amount for e in expenses)

    c = canvas.Canvas(export_path, pagesize=A4)
    _draw_header(c, f"Yearly Report {year}")

    y = 270
    c.setFont("Helvetica-Bold", 11)
    c.drawString(20 * mm, y * mm, "Receipts")
    y -= 7
    c.setFont("Helvetica", 9)
    for p in payments:
        line = f"ID {p.id} | Flat {p.flat_id} | {p.paid_on.isoformat()} | For {p.period_year}-{p.period_month:02d} | {format_inr(p.amount)}"
        c.drawString(20 * mm, y * mm, line)
        y -= 5
        if y < 25:
            c.showPage()
            _draw_header(c, f"Yearly Report {year} (cont.)")
            y = 270
    c.setFont("Helvetica-Bold", 10)
    c.drawString(20 * mm, y * mm, f"Total Receipts: {format_inr(total_receipts)}")
    y -= 10

    c.setFont("Helvetica-Bold", 11)
    c.drawString(20 * mm, y * mm, "Expenses")
    y -= 7
    c.setFont("Helvetica", 9)
    for e in expenses:
        payer = f"Flat {e.paid_by_flat_id}" if e.paid_by_flat_id else "Society"
        line = f"ID {e.id} | {e.category} | {e.spent_on.isoformat()} | {format_inr(e.amount)} | {payer} | {e.description}"
        c.drawString(20 * mm, y * mm, line)
        y -= 5
        if y < 25:
            c.showPage()
            _draw_header(c, f"Yearly Report {year} (cont.)")
            y = 270
    c.setFont("Helvetica-Bold", 10)
    c.drawString(20 * mm, y * mm, f"Total Expenses: {format_inr(total_expenses)}")

    c.showPage()
    c.save()
    return export_path