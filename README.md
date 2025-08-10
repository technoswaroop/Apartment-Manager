# Apartment Expense Manager (Offline Desktop)

An offline desktop application to manage monthly maintenance charges for 7 flats, track expenses (repairs/other), allocate owner-paid repairs against their dues, identify defaulters, and export monthly/yearly reports. Runs locally on Windows without internet.

## Features
- 7 fixed flats with owner management
- Configure monthly maintenance amount and start month/year
- Record maintenance receipts (editable)
- Record expenses (repairs/other). If a flat owner pays a repair expense, it is credited against that flat's dues, and any extra is shown
- Dashboard balance sheet: total receipts, total expenses, corpus balance
- Defaulters view: outstanding per flat up to selected period
- Reports: monthly and yearly (CSV and PDF export)
- Full offline, data stored in local SQLite database file

## Tech Stack
- Python 3.10+
- PySide6 (Qt for Python)
- SQLite (builtin)
- ReportLab (PDF export)
- PyInstaller (Windows packaging)

## Getting Started (Development)

1. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:

   ```bash
   python main.py
   ```

On first run, a local database will be created at `data/apartment_manager.db` with 7 flats initialized.

## Windows Packaging (Offline Installer)

1. Ensure you are on Windows with Python 3.10+ and have run the steps above in an activated venv.

2. Build the executable using PyInstaller:

   ```bat
   build_windows.bat
   ```

This produces a standalone folder at `dist/ApartmentExpenseManager/` with `ApartmentExpenseManager.exe` that runs fully offline.

Optionally, you can ZIP the `dist/ApartmentExpenseManager/` folder as your portable installer. If you need an MSI/EXE installer, tools like Inno Setup or NSIS can wrap the folder into an installer (not required for offline use).

## Data Location

- Database: `data/apartment_manager.db`
- Exports (CSV/PDF): `exports/`

Both folders are created automatically on first run.

## Notes

- Currency is fixed to Indian Rupee (₹) for UI and reports.
- Editing/deleting entries is supported via the respective tabs.
- Reports reflect owner-paid repair credits against their dues.
