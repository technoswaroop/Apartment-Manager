; Inno Setup script for Apartment Manager
#define MyAppName "Apartment Manager"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Apartment Manager"
#define MyAppExeName "ApartmentManager.exe"

[Setup]
AppId={{7B3C4A02-43C1-4E2C-9C1E-2EE9C1E4D1C9}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\ApartmentManager
DisableDirPage=yes
DisableProgramGroupPage=yes
OutputBaseFilename=Setup-ApartmentManager
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
; Update Source: path to your built WPF publish folder
Source: "..\src\Wpf\bin\Release\net8.0-windows\win-x64\publish\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"; Flags: unchecked

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent