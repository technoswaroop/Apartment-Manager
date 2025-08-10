param(
  [string]$Configuration = "Release"
)

$ErrorActionPreference = "Stop"

$solution = Join-Path $PSScriptRoot "..\ApartmentManager.sln"
$wpfProj = Join-Path $PSScriptRoot "..\src\Wpf\ApartmentManager.Wpf.csproj"
$publishDir = Join-Path $PSScriptRoot "..\src\Wpf\bin\$Configuration\net8.0-windows\win-x64\publish"

Write-Host "Restoring..."
dotnet restore $solution

Write-Host "Publishing WPF app..."
dotnet publish $wpfProj -c $Configuration -r win-x64 --self-contained true /p:PublishSingleFile=true /p:IncludeNativeLibrariesForSelfExtract=true

$iss = Join-Path $PSScriptRoot "InnoSetup.iss"
if (-not (Test-Path $iss)) { throw "InnoSetup.iss not found" }

Write-Host "Building installer via Inno Setup..."
$iscc = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if (-not (Test-Path $iscc)) { throw "Inno Setup Compiler not found at $iscc" }

& $iscc $iss

Write-Host "Installer build complete."