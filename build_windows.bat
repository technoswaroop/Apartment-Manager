@echo off
setlocal

REM Ensure venv is activated before running this script
pip install --upgrade pip
pip install -r requirements.txt

REM Clean old builds
if exist build rmdir /S /Q build
if exist dist rmdir /S /Q dist

set APPNAME=ApartmentExpenseManager
set ENTRY=main.py
set ICON=

pyinstaller --name %APPNAME% --noconfirm --clean ^
  --windowed ^
  --add-data "data;data" ^
  --add-data "exports;exports" ^
  %ICON% %ENTRY%

echo.
echo Build complete. Find the app at dist\%APPNAME%\%APPNAME%.exe
endlocal