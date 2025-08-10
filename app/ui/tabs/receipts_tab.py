from __future__ import annotations

from datetime import date

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ...db import Database
from ...models import Payment


class ReceiptsTab(QWidget):
    dataChanged = Signal()

    def __init__(self, db: Database) -> None:
        super().__init__()
        self.db = db
        self.current_edit_id: int | None = None

        # Form
        self.flat_combo = QComboBox()
        self.amount_spin = QSpinBox()
        self.amount_spin.setRange(0, 10_000_000)
        self.paid_on_edit = QDateEdit()
        self.paid_on_edit.setCalendarPopup(True)
        self.paid_on_edit.setDate(date.today())
        self.period_year_spin = QSpinBox()
        self.period_year_spin.setRange(2000, 2100)
        self.period_month_spin = QSpinBox()
        self.period_month_spin.setRange(1, 12)
        self.note_edit = QLineEdit()

        form_layout = QFormLayout()
        form_layout.addRow("Flat", self.flat_combo)
        form_layout.addRow("Amount (₹)", self.amount_spin)
        form_layout.addRow("Paid On", self.paid_on_edit)
        form_layout.addRow("For Year", self.period_year_spin)
        form_layout.addRow("For Month", self.period_month_spin)
        form_layout.addRow("Note", self.note_edit)

        self.btn_add = QPushButton("Add Receipt")
        self.btn_update = QPushButton("Update")
        self.btn_delete = QPushButton("Delete")
        self.btn_clear = QPushButton("Clear")
        self.btn_update.setEnabled(False)
        self.btn_delete.setEnabled(False)

        btns = QHBoxLayout()
        btns.addWidget(self.btn_add)
        btns.addWidget(self.btn_update)
        btns.addWidget(self.btn_delete)
        btns.addWidget(self.btn_clear)

        form_group = QGroupBox("Add / Edit Receipt")
        form_v = QVBoxLayout()
        form_v.addLayout(form_layout)
        form_v.addLayout(btns)
        form_group.setLayout(form_v)

        # Table
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["ID", "Flat", "Amount", "Paid On", "For Year", "For Month", "Note"])
        self.table.setSelectionBehavior(self.table.SelectRows)
        self.table.setEditTriggers(self.table.NoEditTriggers)
        self.table.cellClicked.connect(self.on_row_selected)

        layout = QVBoxLayout()
        layout.addWidget(form_group)
        layout.addWidget(QLabel("All Receipts"))
        layout.addWidget(self.table)
        self.setLayout(layout)

        self.btn_add.clicked.connect(self.add_receipt)
        self.btn_update.clicked.connect(self.update_receipt)
        self.btn_delete.clicked.connect(self.delete_receipt)
        self.btn_clear.clicked.connect(self.clear_form)

        self.refresh_flats()

    def refresh(self) -> None:
        self.refresh_table()
        self.refresh_flats()

    def refresh_flats(self) -> None:
        flats = self.db.list_flats()
        current = self.flat_combo.currentData()
        self.flat_combo.blockSignals(True)
        self.flat_combo.clear()
        for f in flats:
            display = f"{f.code} - {f.owner_name}" if f.owner_name else f.code
            self.flat_combo.addItem(display, f.id)
        self.flat_combo.blockSignals(False)
        # restore selection
        if current is not None:
            idx = self.flat_combo.findData(current)
            if idx >= 0:
                self.flat_combo.setCurrentIndex(idx)

    def refresh_table(self) -> None:
        payments = self.db.list_payments()
        self.table.setRowCount(len(payments))
        for row, p in enumerate(payments):
            self.table.setItem(row, 0, QTableWidgetItem(str(p.id)))
            self.table.setItem(row, 1, QTableWidgetItem(str(p.flat_id)))
            self.table.setItem(row, 2, QTableWidgetItem(str(p.amount)))
            self.table.setItem(row, 3, QTableWidgetItem(p.paid_on.isoformat()))
            self.table.setItem(row, 4, QTableWidgetItem(str(p.period_year)))
            self.table.setItem(row, 5, QTableWidgetItem(str(p.period_month)))
            self.table.setItem(row, 6, QTableWidgetItem(p.note))
        self.table.resizeColumnsToContents()

    def on_row_selected(self, row: int, col: int) -> None:
        id_item = self.table.item(row, 0)
        if not id_item:
            return
        self.current_edit_id = int(id_item.text())
        flat_id = int(self.table.item(row, 1).text())
        amount = int(self.table.item(row, 2).text())
        paid_on = date.fromisoformat(self.table.item(row, 3).text())
        per_year = int(self.table.item(row, 4).text())
        per_month = int(self.table.item(row, 5).text())
        note = self.table.item(row, 6).text()

        idx = self.flat_combo.findData(flat_id)
        if idx >= 0:
            self.flat_combo.setCurrentIndex(idx)
        self.amount_spin.setValue(amount)
        self.paid_on_edit.setDate(paid_on)
        self.period_year_spin.setValue(per_year)
        self.period_month_spin.setValue(per_month)
        self.note_edit.setText(note)
        self.btn_update.setEnabled(True)
        self.btn_delete.setEnabled(True)

    def clear_form(self) -> None:
        self.current_edit_id = None
        self.amount_spin.setValue(0)
        self.paid_on_edit.setDate(date.today())
        settings = self.db.get_settings()
        self.period_year_spin.setValue(settings.start_year)
        self.period_month_spin.setValue(settings.start_month)
        self.note_edit.clear()
        self.btn_update.setEnabled(False)
        self.btn_delete.setEnabled(False)
        if self.flat_combo.count() > 0:
            self.flat_combo.setCurrentIndex(0)

    def add_receipt(self) -> None:
        flat_id = int(self.flat_combo.currentData())
        amount = int(self.amount_spin.value())
        paid_on = self.paid_on_edit.date().toPython()
        period_year = int(self.period_year_spin.value())
        period_month = int(self.period_month_spin.value())
        note = self.note_edit.text()
        if amount <= 0:
            return
        self.db.add_payment(flat_id, amount, paid_on, period_year, period_month, note)
        self.clear_form()
        self.refresh_table()
        self.dataChanged.emit()

    def update_receipt(self) -> None:
        if self.current_edit_id is None:
            return
        flat_id = int(self.flat_combo.currentData())
        amount = int(self.amount_spin.value())
        paid_on = self.paid_on_edit.date().toPython()
        period_year = int(self.period_year_spin.value())
        period_month = int(self.period_month_spin.value())
        note = self.note_edit.text()
        self.db.update_payment(self.current_edit_id, flat_id, amount, paid_on, period_year, period_month, note)
        self.clear_form()
        self.refresh_table()
        self.dataChanged.emit()

    def delete_receipt(self) -> None:
        if self.current_edit_id is None:
            return
        self.db.delete_payment(self.current_edit_id)
        self.clear_form()
        self.refresh_table()
        self.dataChanged.emit()