from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ...db import Database


class SettingsTab(QWidget):
    dataChanged = Signal()

    def __init__(self, db: Database) -> None:
        super().__init__()
        self.db = db

        self.monthly_fee = QSpinBox(); self.monthly_fee.setRange(0, 1000000)
        self.start_year = QSpinBox(); self.start_year.setRange(2000, 2100)
        self.start_month = QSpinBox(); self.start_month.setRange(1, 12)

        f = QFormLayout()
        f.addRow("Monthly Maintenance (₹)", self.monthly_fee)
        f.addRow("Start Year", self.start_year)
        f.addRow("Start Month", self.start_month)

        self.btn_save = QPushButton("Save Settings")
        v1 = QVBoxLayout(); v1.addLayout(f); v1.addWidget(self.btn_save)
        g1 = QGroupBox("Maintenance Settings"); g1.setLayout(v1)

        self.owners_table = QTableWidget(7, 3)
        self.owners_table.setHorizontalHeaderLabels(["Flat ID", "Flat Code", "Owner Name"])
        self.owners_table.setEditTriggers(self.owners_table.DoubleClicked | self.owners_table.EditKeyPressed | self.owners_table.SelectedClicked)

        v2 = QVBoxLayout(); v2.addWidget(self.owners_table)
        g2 = QGroupBox("Flat Owners"); g2.setLayout(v2)

        layout = QVBoxLayout()
        layout.addWidget(g1)
        layout.addWidget(g2)
        self.setLayout(layout)

        self.btn_save.clicked.connect(self.save_settings)
        self.owners_table.itemChanged.connect(self.on_owner_changed)

        self.refresh()

    def refresh(self) -> None:
        s = self.db.get_settings()
        self.monthly_fee.setValue(s.monthly_fee)
        self.start_year.setValue(s.start_year)
        self.start_month.setValue(s.start_month)

        flats = self.db.list_flats()
        self.owners_table.blockSignals(True)
        self.owners_table.setRowCount(len(flats))
        for i, f in enumerate(flats):
            self.owners_table.setItem(i, 0, QTableWidgetItem(str(f.id)))
            self.owners_table.item(i, 0).setFlags(self.owners_table.item(i, 0).flags() & ~Qt.ItemIsEditable)
            self.owners_table.setItem(i, 1, QTableWidgetItem(f.code))
            self.owners_table.item(i, 1).setFlags(self.owners_table.item(i, 1).flags() & ~Qt.ItemIsEditable)
            self.owners_table.setItem(i, 2, QTableWidgetItem(f.owner_name))
        self.owners_table.resizeColumnsToContents()
        self.owners_table.blockSignals(False)

    def save_settings(self) -> None:
        self.db.update_settings(
            int(self.monthly_fee.value()), int(self.start_year.value()), int(self.start_month.value())
        )
        self.dataChanged.emit()

    def on_owner_changed(self, item) -> None:
        if item.column() != 2:
            return
        row = item.row()
        flat_id = int(self.owners_table.item(row, 0).text())
        owner_name = item.text()
        self.db.update_flat_owner(flat_id, owner_name)
        self.dataChanged.emit()