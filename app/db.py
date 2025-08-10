from __future__ import annotations

import sqlite3
from dataclasses import asdict
from datetime import date, datetime
from typing import Dict, List, Optional, Tuple

from .models import Expense, Flat, Payment, Settings
from .utils import iterate_periods_inclusive


class Database:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def initialize(self) -> None:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS flats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT NOT NULL UNIQUE,
                    owner_name TEXT NOT NULL DEFAULT ''
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    monthly_fee INTEGER NOT NULL,
                    start_year INTEGER NOT NULL,
                    start_month INTEGER NOT NULL
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    flat_id INTEGER NOT NULL REFERENCES flats(id) ON DELETE CASCADE,
                    amount INTEGER NOT NULL,
                    paid_on TEXT NOT NULL,
                    period_year INTEGER NOT NULL,
                    period_month INTEGER NOT NULL,
                    note TEXT NOT NULL DEFAULT ''
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    amount INTEGER NOT NULL,
                    spent_on TEXT NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    paid_by_flat_id INTEGER NULL REFERENCES flats(id) ON DELETE SET NULL
                )
                """
            )
            # Seed flats if empty
            cur.execute("SELECT COUNT(1) AS c FROM flats")
            if cur.fetchone()[0] == 0:
                for i in range(1, 8):
                    code = f"F{i}"
                    cur.execute("INSERT INTO flats (code, owner_name) VALUES (?, ?)", (code, f""))
            # Seed settings if empty
            cur.execute("SELECT COUNT(1) FROM settings")
            if cur.fetchone()[0] == 0:
                today = date.today()
                cur.execute(
                    "INSERT INTO settings (id, monthly_fee, start_year, start_month) VALUES (1, ?, ?, ?)",
                    (1000, today.year, today.month),
                )
            conn.commit()

    # Flats
    def list_flats(self) -> List[Flat]:
        with self._connect() as conn:
            rows = conn.execute("SELECT id, code, owner_name FROM flats ORDER BY id").fetchall()
            return [Flat(id=r["id"], code=r["code"], owner_name=r["owner_name"]) for r in rows]

    def update_flat_owner(self, flat_id: int, owner_name: str) -> None:
        with self._connect() as conn:
            conn.execute("UPDATE flats SET owner_name = ? WHERE id = ?", (owner_name, flat_id))
            conn.commit()

    # Settings
    def get_settings(self) -> Settings:
        with self._connect() as conn:
            r = conn.execute("SELECT monthly_fee, start_year, start_month FROM settings WHERE id = 1").fetchone()
            return Settings(monthly_fee=r["monthly_fee"], start_year=r["start_year"], start_month=r["start_month"])

    def update_settings(self, monthly_fee: int, start_year: int, start_month: int) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE settings SET monthly_fee = ?, start_year = ?, start_month = ? WHERE id = 1",
                (monthly_fee, start_year, start_month),
            )
            conn.commit()

    # Payments
    def add_payment(self, flat_id: int, amount: int, paid_on: date, period_year: int, period_month: int, note: str) -> int:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO payments (flat_id, amount, paid_on, period_year, period_month, note) VALUES (?, ?, ?, ?, ?, ?)",
                (flat_id, amount, paid_on.isoformat(), period_year, period_month, note),
            )
            conn.commit()
            return int(cur.lastrowid)

    def update_payment(self, payment_id: int, flat_id: int, amount: int, paid_on: date, period_year: int, period_month: int, note: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE payments
                SET flat_id = ?, amount = ?, paid_on = ?, period_year = ?, period_month = ?, note = ?
                WHERE id = ?
                """,
                (flat_id, amount, paid_on.isoformat(), period_year, period_month, note, payment_id),
            )
            conn.commit()

    def delete_payment(self, payment_id: int) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM payments WHERE id = ?", (payment_id,))
            conn.commit()

    def list_payments(self) -> List[Payment]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, flat_id, amount, paid_on, period_year, period_month, note FROM payments ORDER BY date(paid_on) DESC, id DESC"
            ).fetchall()
            result: List[Payment] = []
            for r in rows:
                result.append(
                    Payment(
                        id=r["id"],
                        flat_id=r["flat_id"],
                        amount=r["amount"],
                        paid_on=date.fromisoformat(r["paid_on"]),
                        period_year=r["period_year"],
                        period_month=r["period_month"],
                        note=r["note"],
                    )
                )
            return result

    # Expenses
    def add_expense(
        self,
        category: str,
        amount: int,
        spent_on: date,
        description: str,
        paid_by_flat_id: Optional[int],
    ) -> int:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO expenses (category, amount, spent_on, description, paid_by_flat_id) VALUES (?, ?, ?, ?, ?)",
                (category, amount, spent_on.isoformat(), description, paid_by_flat_id),
            )
            conn.commit()
            return int(cur.lastrowid)

    def update_expense(
        self,
        expense_id: int,
        category: str,
        amount: int,
        spent_on: date,
        description: str,
        paid_by_flat_id: Optional[int],
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE expenses
                SET category = ?, amount = ?, spent_on = ?, description = ?, paid_by_flat_id = ?
                WHERE id = ?
                """,
                (category, amount, spent_on.isoformat(), description, paid_by_flat_id, expense_id),
            )
            conn.commit()

    def delete_expense(self, expense_id: int) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
            conn.commit()

    def list_expenses(self) -> List[Expense]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, category, amount, spent_on, description, paid_by_flat_id FROM expenses ORDER BY date(spent_on) DESC, id DESC"
            ).fetchall()
            result: List[Expense] = []
            for r in rows:
                result.append(
                    Expense(
                        id=r["id"],
                        category=r["category"],
                        amount=r["amount"],
                        spent_on=date.fromisoformat(r["spent_on"]),
                        description=r["description"],
                        paid_by_flat_id=r["paid_by_flat_id"],
                    )
                )
            return result

    # Aggregations
    def compute_receipts_totals(self) -> int:
        with self._connect() as conn:
            row = conn.execute("SELECT COALESCE(SUM(amount),0) AS s FROM payments").fetchone()
            return int(row[0])

    def compute_expenses_totals(self) -> Tuple[int, int, int]:
        with self._connect() as conn:
            row_all = conn.execute("SELECT COALESCE(SUM(amount),0) FROM expenses").fetchone()
            row_society = conn.execute("SELECT COALESCE(SUM(amount),0) FROM expenses WHERE paid_by_flat_id IS NULL").fetchone()
            row_owner = conn.execute("SELECT COALESCE(SUM(amount),0) FROM expenses WHERE paid_by_flat_id IS NOT NULL").fetchone()
            return int(row_all[0]), int(row_society[0]), int(row_owner[0])

    def compute_corpus_balance(self) -> int:
        receipts = self.compute_receipts_totals()
        _, total_society, _ = self.compute_expenses_totals()
        return receipts - total_society

    def get_owner_credits(self) -> Dict[int, int]:
        # credits from owner-paid expenses
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT paid_by_flat_id AS flat_id, COALESCE(SUM(amount),0) AS s FROM expenses WHERE paid_by_flat_id IS NOT NULL GROUP BY paid_by_flat_id"
            ).fetchall()
            return {int(r["flat_id"]): int(r["s"]) for r in rows if r["flat_id"] is not None}

    def get_payments_by_flat(self) -> Dict[int, int]:
        with self._connect() as conn:
            rows = conn.execute("SELECT flat_id, COALESCE(SUM(amount),0) AS s FROM payments GROUP BY flat_id").fetchall()
            return {int(r["flat_id"]): int(r["s"]) for r in rows}

    def compute_dues_upto(self, end_year: int, end_month: int) -> Dict[int, Dict[str, int]]:
        settings = self.get_settings()
        flats = self.list_flats()
        payments = self.get_payments_by_flat()
        owner_credits = self.get_owner_credits()

        # Compute number of months
        num_months = 0
        for _ in iterate_periods_inclusive(settings.start_year, settings.start_month, end_year, end_month):
            num_months += 1

        dues_per_flat = settings.monthly_fee * num_months
        result: Dict[int, Dict[str, int]] = {}
        for f in flats:
            paid = payments.get(f.id, 0)
            credit = owner_credits.get(f.id, 0)
            total_credit = paid + credit
            outstanding = dues_per_flat - total_credit
            result[f.id] = {
                "dues": dues_per_flat,
                "payments": paid,
                "owner_credit": credit,
                "outstanding": outstanding,
                "advance": -outstanding if outstanding < 0 else 0,
            }
        return result

    # Reporting helpers
    def list_payments_in_month(self, year: int, month: int) -> List[Payment]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, flat_id, amount, paid_on, period_year, period_month, note FROM payments WHERE period_year = ? AND period_month = ? ORDER BY date(paid_on) ASC, id ASC",
                (year, month),
            ).fetchall()
            result: List[Payment] = []
            for r in rows:
                result.append(
                    Payment(
                        id=r["id"],
                        flat_id=r["flat_id"],
                        amount=r["amount"],
                        paid_on=date.fromisoformat(r["paid_on"]),
                        period_year=r["period_year"],
                        period_month=r["period_month"],
                        note=r["note"],
                    )
                )
            return result

    def list_expenses_in_month(self, year: int, month: int) -> List[Expense]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, category, amount, spent_on, description, paid_by_flat_id FROM expenses WHERE strftime('%Y', spent_on) = ? AND strftime('%m', spent_on) = ? ORDER BY date(spent_on) ASC, id ASC",
                (f"{year:04d}", f"{month:02d}"),
            ).fetchall()
            result: List[Expense] = []
            for r in rows:
                result.append(
                    Expense(
                        id=r["id"],
                        category=r["category"],
                        amount=r["amount"],
                        spent_on=date.fromisoformat(r["spent_on"]),
                        description=r["description"],
                        paid_by_flat_id=r["paid_by_flat_id"],
                    )
                )
            return result

    def list_payments_in_year(self, year: int) -> List[Payment]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, flat_id, amount, paid_on, period_year, period_month, note FROM payments WHERE period_year = ? ORDER BY period_month ASC, date(paid_on) ASC, id ASC",
                (year,),
            ).fetchall()
            result: List[Payment] = []
            for r in rows:
                result.append(
                    Payment(
                        id=r["id"],
                        flat_id=r["flat_id"],
                        amount=r["amount"],
                        paid_on=date.fromisoformat(r["paid_on"]),
                        period_year=r["period_year"],
                        period_month=r["period_month"],
                        note=r["note"],
                    )
                )
            return result

    def list_expenses_in_year(self, year: int) -> List[Expense]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, category, amount, spent_on, description, paid_by_flat_id FROM expenses WHERE strftime('%Y', spent_on) = ? ORDER BY date(spent_on) ASC, id ASC",
                (f"{year:04d}",),
            ).fetchall()
            result: List[Expense] = []
            for r in rows:
                result.append(
                    Expense(
                        id=r["id"],
                        category=r["category"],
                        amount=r["amount"],
                        spent_on=date.fromisoformat(r["spent_on"]),
                        description=r["description"],
                        paid_by_flat_id=r["paid_by_flat_id"],
                    )
                )
            return result