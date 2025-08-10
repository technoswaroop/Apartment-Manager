from __future__ import annotations

from datetime import date

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QComboBox, QFormLayout, QLabel, QSpinBox, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from ...db import Database
from ...utils import format_inr


class DefaultersTab(QWidget):
    def __init__(self, db: Database) -> None:
        super().__init__()
        self.db = db

        settings = self.db.get_settings()
        self.year_spin = QSpinBox()
        self.year_spin.setRange(2000, 2100)
        self.year_spin.setValue(settings.start_year)
        self.month_spin = QSpinBox()
        self.month_spin.setRange(1, 12)
        self.month_spin.setValue(settings.start_month)

        form = QFormLayout()
        form.addRow("Up to Year", self.year_spin)
        form.addRow("Up to Month", self.month_spin)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(
            [
                "Flat",
                "Owner",
                "Dues",
                "Payments",
                "Owner Credit",
                "Outstanding",
                "Advance",
            ]
        )
        self.table.setEditTriggers(self.table.NoEditTriggers)
        self.table.setSelectionBehavior(self.table.SelectRows)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(QLabel("Defaulters / Balances"))
        layout.addWidget(self.table)
        self.setLayout(layout)

        self.year_spin.valueChanged.connect(self.refresh)
        self.month_spin.valueChanged.connect(self.refresh)

    def refresh(self) -> None:
        end_year = int(self.year_spin.value())
        end_month = int(self.month_spin.value())
        stats = self.db.compute_dues_upto(end_year, end_month)
        flats = self.db.list_flats()
        rows = []
        for f in flats:
            s = stats[f.id]
            rows.append(
                (
                    f.code,
                    f.owner_name,
                    s["dues"],
                    s["payments"],
                    s["owner_credit"],
                    s["outstanding"],
                    s["advance"],
                )
            )
        self.table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            for j, val in enumerate(r):
                item = QTableWidgetItem(str(val) if isinstance(val, int) else val)
                if j >= 2:
                    item.setText(format_inr(int(val)))
                    if j == 5 and int(val) > 0:
                        item.setForeground(QColor("red"))
                self.table.setItem(i, j, item)
        self.table.resizeColumnsToContents()