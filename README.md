# Apartment Manager (WPF + SQLite)

A Windows desktop application for managing apartment expenses across 7 flats: maintenance, repairs, defaulters, and financial reporting in INR.

## Projects
- `src/Core` — domain models
- `src/Data` — EF Core (SQLite) DbContext and services
- `src/Wpf` — WPF app (net8.0-windows)
- `tests` — unit tests

## Build
- Windows 10/11 with .NET 8 SDK and Visual Studio 2022 (Desktop development with C#)
- Open `ApartmentManager.sln` and set `ApartmentManager.Wpf` as startup project
- Build and run

## First Run
- DB file: `%LOCALAPPDATA%\ApartmentManager\apartment.db`
- App seeds 7 flats `F1..F7`

## Packaging

### Option A: MSIX Packaging (Visual Studio)
1. In VS, add Windows App Packaging Project (MSIX) targeting `ApartmentManager.Wpf`
2. Configure Publisher, signing (or developer certificate)
3. Build MSIX package; install on Windows 10/11

### Option B: Inno Setup (MSI-like Installer)
1. Install Inno Setup
2. Use the provided `installer\InnoSetup.iss` script
3. Build installer; run `Setup-ApartmentManager.exe`

## Features
- Maintenance setup and payments
- Repair expense allocation (equal across 7 flats)
- Automatic credit to payer
- Defaulter list and CSV export
- Financial reports (Balance Sheet, Income, Cash Flow) CSV export
- INR formatting, backup/restore

## Tests
```
dotnet test ApartmentManager.sln
```
