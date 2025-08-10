from __future__ import annotations

from datetime import date

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from ...db import Database
from ...utils import format_inr


class DashboardTab(QWidget):
    def __init__(self, db: Database) -> None:
        super().__init__()
        self.db = db

        self.lbl_receipts = QLabel()
        self.lbl_expenses_society = QLabel()
        self.lbl_expenses_owner = QLabel()
        self.lbl_corpus = QLabel()

        layout = QVBoxLayout()
        for w in [self.lbl_receipts, self.lbl_expenses_society, self.lbl_expenses_owner, self.lbl_corpus]:
            w.setAlignment(Qt.AlignLeft)
            w.setStyleSheet("font-size: 16px; margin: 4px 0;")
            layout.addWidget(w)

        self.setLayout(layout)

    def refresh(self) -> None:
        receipts = self.db.compute_receipts_totals()
        total_expenses, society_expenses, owner_expenses = self.db.compute_expenses_totals()
        corpus = self.db.compute_corpus_balance()

        self.lbl_receipts.setText(f"Total Receipts: {format_inr(receipts)}")
        self.lbl_expenses_society.setText(f"Expenses (Society Paid): {format_inr(society_expenses)}")
        self.lbl_expenses_owner.setText(f"Expenses (Owner Paid): {format_inr(owner_expenses)}")
        self.lbl_corpus.setText(f"Corpus Balance: {format_inr(corpus)}")