from __future__ import annotations

from datetime import date
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QStatusBar, QTabWidget

from ..db import Database
from ..utils import format_inr
from .tabs.dashboard_tab import DashboardTab
from .tabs.defaulters_tab import DefaultersTab
from .tabs.expenses_tab import ExpensesTab
from .tabs.receipts_tab import ReceiptsTab
from .tabs.reports_tab import ReportsTab
from .tabs.settings_tab import SettingsTab


class MainWindow(QMainWindow):
    def __init__(self, db: Database) -> None:
        super().__init__()
        self.db = db
        self.setWindowTitle("Apartment Expense Manager")

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.dashboard_tab = DashboardTab(db)
        self.receipts_tab = ReceiptsTab(db)
        self.expenses_tab = ExpensesTab(db)
        self.defaulters_tab = DefaultersTab(db)
        self.reports_tab = ReportsTab(db)
        self.settings_tab = SettingsTab(db)

        self.tabs.addTab(self.dashboard_tab, "Dashboard")
        self.tabs.addTab(self.receipts_tab, "Receipts")
        self.tabs.addTab(self.expenses_tab, "Expenses")
        self.tabs.addTab(self.defaulters_tab, "Defaulters")
        self.tabs.addTab(self.reports_tab, "Reports")
        self.tabs.addTab(self.settings_tab, "Settings")

        self.status = QStatusBar()
        self.setStatusBar(self.status)

        # Apply minimal modern style
        self.setStyleSheet(
            """
            QWidget { font-family: 'Segoe UI', 'Noto Sans', Arial; font-size: 12px; }
            QMainWindow { background: #101216; color: #E6E6E6; }
            QTabWidget::pane { border: 1px solid #2a2e35; background: #0f1114; }
            QTabBar::tab { background: #161a20; color: #cfd3da; padding: 8px 14px; border: 1px solid #2a2e35; border-bottom: none; }
            QTabBar::tab:selected { background: #1e2430; color: #ffffff; }
            QGroupBox { border: 1px solid #2a2e35; border-radius: 6px; margin-top: 10px; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }
            QLabel { color: #d7dbe2; }
            QLineEdit, QSpinBox, QDateEdit, QComboBox { background: #0f1114; color: #e6e6e6; border: 1px solid #2a2e35; padding: 4px 6px; border-radius: 4px; }
            QPushButton { background: #2b7cff; color: #ffffff; padding: 6px 12px; border: none; border-radius: 4px; }
            QPushButton:hover { background: #1f6ae0; }
            QPushButton:disabled { background: #3a3f47; color: #9aa0a6; }
            QTableWidget { gridline-color: #2a2e35; background: #0f1114; color: #e6e6e6; }
            QHeaderView::section { background: #161a20; color: #cfd3da; border: 1px solid #2a2e35; padding: 4px; }
            QStatusBar { background: #0f1114; color: #cfd3da; }
            """
        )

        # Wire refresh events
        self.receipts_tab.dataChanged.connect(self.refresh_all)
        self.expenses_tab.dataChanged.connect(self.refresh_all)
        self.settings_tab.dataChanged.connect(self.refresh_all)

        self.refresh_all()

    def refresh_all(self) -> None:
        self.dashboard_tab.refresh()
        self.receipts_tab.refresh()
        self.expenses_tab.refresh()
        self.defaulters_tab.refresh()
        self.reports_tab.refresh()
        self.settings_tab.refresh()
        receipts = self.db.compute_receipts_totals()
        _, society, owner_paid = self.db.compute_expenses_totals()
        corpus = self.db.compute_corpus_balance()
        self.status.showMessage(
            f"Receipts: {format_inr(receipts)} | Expenses (Society): {format_inr(society)} | Owner-paid: {format_inr(owner_paid)} | Corpus: {format_inr(corpus)}"
        )