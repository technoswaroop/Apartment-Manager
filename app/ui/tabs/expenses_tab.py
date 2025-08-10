from __future__ import annotations

from datetime import date

from PySide6.QtCore import Qt, Signal
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


class ExpensesTab(QWidget):
    dataChanged = Signal()

    def __init__(self, db: Database) -> None:
        super().__init__()
        self.db = db
        self.current_edit_id: int | None = None

        # Form fields
        self.category_combo = QComboBox()
        self.category_combo.addItems(["Repairs", "Other"])
        self.amount_spin = QSpinBox()
        self.amount_spin.setRange(0, 20_000_000)
        self.spent_on_edit = QDateEdit()
        self.spent_on_edit.setCalendarPopup(True)
        self.spent_on_edit.setDate(date.today())
        self.description_edit = QLineEdit()
        self.paid_by_flat_combo = QComboBox()
        self.paid_by_flat_combo.addItem("Society (from corpus)", None)

        form = QFormLayout()
        form.addRow("Category", self.category_combo)
        form.addRow("Amount (₹)", self.amount_spin)
        form.addRow("Spent On", self.spent_on_edit)
        form.addRow("Description", self.description_edit)
        form.addRow("Paid By", self.paid_by_flat_combo)

        self.btn_add = QPushButton("Add Expense")
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

        group = QGroupBox("Add / Edit Expense")
        v = QVBoxLayout()
        v.addLayout(form)
        v.addLayout(btns)
        group.setLayout(v)

        # Table
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["ID", "Category", "Amount", "Spent On", "Description", "Paid By Flat ID"])
        self.table.setSelectionBehavior(self.table.SelectRows)
        self.table.setEditTriggers(self.table.NoEditTriggers)
        self.table.cellClicked.connect(self.on_row_selected)

        layout = QVBoxLayout()
        layout.addWidget(group)
        layout.addWidget(QLabel("All Expenses"))
        layout.addWidget(self.table)
        self.setLayout(layout)

        self.btn_add.clicked.connect(self.add_expense)
        self.btn_update.clicked.connect(self.update_expense)
        self.btn_delete.clicked.connect(self.delete_expense)
        self.btn_clear.clicked.connect(self.clear_form)

        self.refresh_flats()

    def refresh(self) -> None:
        self.refresh_table()
        self.refresh_flats()

    def refresh_flats(self) -> None:
        flats = self.db.list_flats()
        self.paid_by_flat_combo.blockSignals(True)
        current = self.paid_by_flat_combo.currentData()
        self.paid_by_flat_combo.clear()
        self.paid_by_flat_combo.addItem("Society (from corpus)", None)
        for f in flats:
            display = f"{f.code} - {f.owner_name}" if f.owner_name else f.code
            self.paid_by_flat_combo.addItem(display, f.id)
        self.paid_by_flat_combo.blockSignals(False)
        if current is not None:
            idx = self.paid_by_flat_combo.findData(current)
            if idx >= 0:
                self.paid_by_flat_combo.setCurrentIndex(idx)

    def refresh_table(self) -> None:
        expenses = self.db.list_expenses()
        self.table.setRowCount(len(expenses))
        for row, e in enumerate(expenses):
            self.table.setItem(row, 0, QTableWidgetItem(str(e.id)))
            self.table.setItem(row, 1, QTableWidgetItem(e.category))
            self.table.setItem(row, 2, QTableWidgetItem(str(e.amount)))
            self.table.setItem(row, 3, QTableWidgetItem(e.spent_on.isoformat()))
            self.table.setItem(row, 4, QTableWidgetItem(e.description))
            self.table.setItem(row, 5, QTableWidgetItem(str(e.paid_by_flat_id) if e.paid_by_flat_id else "-"))
        self.table.resizeColumnsToContents()

    def on_row_selected(self, row: int, col: int) -> None:
        id_item = self.table.item(row, 0)
        if not id_item:
            return
        self.current_edit_id = int(id_item.text())
        category = self.table.item(row, 1).text()
        amount = int(self.table.item(row, 2).text())
        spent_on = date.fromisoformat(self.table.item(row, 3).text())
        description = self.table.item(row, 4).text()
        paid_by_text = self.table.item(row, 5).text()
        paid_by = None if paid_by_text == "-" else int(paid_by_text)

        idx_cat = self.category_combo.findText(category)
        if idx_cat >= 0:
            self.category_combo.setCurrentIndex(idx_cat)
        self.amount_spin.setValue(amount)
        self.spent_on_edit.setDate(spent_on)
        self.description_edit.setText(description)
        idx = self.paid_by_flat_combo.findData(paid_by)
        if idx >= 0:
            self.paid_by_flat_combo.setCurrentIndex(idx)
        self.btn_update.setEnabled(True)
        self.btn_delete.setEnabled(True)

    def clear_form(self) -> None:
        self.current_edit_id = None
        self.category_combo.setCurrentIndex(0)
        self.amount_spin.setValue(0)
        self.spent_on_edit.setDate(date.today())
        self.description_edit.clear()
        self.paid_by_flat_combo.setCurrentIndex(0)
        self.btn_update.setEnabled(False)
        self.btn_delete.setEnabled(False)

    def add_expense(self) -> None:
        category = self.category_combo.currentText()
        amount = int(self.amount_spin.value())
        spent_on = self.spent_on_edit.date().toPython()
        description = self.description_edit.text()
        paid_by_flat_id = self.paid_by_flat_combo.currentData()
        if amount <= 0:
            return
        self.db.add_expense(category, amount, spent_on, description, paid_by_flat_id)
        self.clear_form()
        self.refresh_table()
        self.dataChanged.emit()

    def update_expense(self) -> None:
        if self.current_edit_id is None:
            return
        category = self.category_combo.currentText()
        amount = int(self.amount_spin.value())
        spent_on = self.spent_on_edit.date().toPython()
        description = self.description_edit.text()
        paid_by_flat_id = self.paid_by_flat_combo.currentData()
        self.db.update_expense(self.current_edit_id, category, amount, spent_on, description, paid_by_flat_id)
        self.clear_form()
        self.refresh_table()
        self.dataChanged.emit()

    def delete_expense(self) -> None:
        if self.current_edit_id is None:
            return
        self.db.delete_expense(self.current_edit_id)
        self.clear_form()
        self.refresh_table()
        self.dataChanged.emit()