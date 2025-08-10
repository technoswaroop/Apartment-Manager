import os
import sys

from PySide6.QtWidgets import QApplication
from app.db import Database
from app.ui.main_window import MainWindow


def ensure_directories() -> None:
    os.makedirs("data", exist_ok=True)
    os.makedirs("exports", exist_ok=True)


def main() -> int:
    ensure_directories()
    db = Database(os.path.join("data", "apartment_manager.db"))
    db.initialize()

    app = QApplication(sys.argv)
    app.setApplicationName("Apartment Expense Manager")

    window = MainWindow(db)
    window.resize(1080, 720)
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())