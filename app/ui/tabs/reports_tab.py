from __future__ import annotations

import os
from datetime import date

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ...db import Database
from ...reporting import export_month_csv, export_month_pdf, export_year_csv, export_year_pdf


class ReportsTab(QWidget):
    def __init__(self, db: Database) -> None:
        super().__init__()
        self.db = db

        today = date.today()
        self.month_spin = QSpinBox(); self.month_spin.setRange(1, 12); self.month_spin.setValue(today.month)
        self.year_spin = QSpinBox(); self.year_spin.setRange(2000, 2100); self.year_spin.setValue(today.year)
        self.year_only_spin = QSpinBox(); self.year_only_spin.setRange(2000, 2100); self.year_only_spin.setValue(today.year)

        form_month = QFormLayout()
        form_month.addRow("Month", self.month_spin)
        form_month.addRow("Year", self.year_spin)
        g_month = QGroupBox("Monthly Report")
        v1 = QVBoxLayout(); v1.addLayout(form_month)
        self.btn_m_csv = QPushButton("Export CSV")
        self.btn_m_pdf = QPushButton("Export PDF")
        row = QHBoxLayout(); row.addWidget(self.btn_m_csv); row.addWidget(self.btn_m_pdf); v1.addLayout(row)
        g_month.setLayout(v1)

        form_year = QFormLayout()
        form_year.addRow("Year", self.year_only_spin)
        g_year = QGroupBox("Yearly Report")
        v2 = QVBoxLayout(); v2.addLayout(form_year)
        self.btn_y_csv = QPushButton("Export CSV")
        self.btn_y_pdf = QPushButton("Export PDF")
        row2 = QHBoxLayout(); row2.addWidget(self.btn_y_csv); row2.addWidget(self.btn_y_pdf); v2.addLayout(row2)
        g_year.setLayout(v2)

        self.lbl_status = QLabel("")
        self.lbl_status.setWordWrap(True)
        layout = QVBoxLayout()
        layout.addWidget(g_month)
        layout.addWidget(g_year)
        layout.addWidget(self.lbl_status)
        self.setLayout(layout)

        self.btn_m_csv.clicked.connect(self.on_export_month_csv)
        self.btn_m_pdf.clicked.connect(self.on_export_month_pdf)
        self.btn_y_csv.clicked.connect(self.on_export_year_csv)
        self.btn_y_pdf.clicked.connect(self.on_export_year_pdf)

    def refresh(self) -> None:
        pass

    def on_export_month_csv(self) -> None:
        y = int(self.year_spin.value()); m = int(self.month_spin.value())
        path = os.path.join("exports", f"monthly_{y}_{m:02d}.csv")
        export_month_csv(self.db, y, m, path)
        self.lbl_status.setText(f"Saved: {path}")

    def on_export_month_pdf(self) -> None:
        y = int(self.year_spin.value()); m = int(self.month_spin.value())
        path = os.path.join("exports", f"monthly_{y}_{m:02d}.pdf")
        export_month_pdf(self.db, y, m, path)
        self.lbl_status.setText(f"Saved: {path}")

    def on_export_year_csv(self) -> None:
        y = int(self.year_only_spin.value())
        path = os.path.join("exports", f"yearly_{y}.csv")
        export_year_csv(self.db, y, path)
        self.lbl_status.setText(f"Saved: {path}")

    def on_export_year_pdf(self) -> None:
        y = int(self.year_only_spin.value())
        path = os.path.join("exports", f"yearly_{y}.pdf")
        export_year_pdf(self.db, y, path)
        self.lbl_status.setText(f"Saved: {path}")