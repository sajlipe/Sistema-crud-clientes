[Setup]
AppId=SistemaCRUD
AppName=Sistema de Gerenciamento de Clientes e Pedidos
AppVersion=2.0
AppPublisher=SistemaCRUD
DefaultDirName={pf}\SistemaCRUD
DefaultGroupName=SistemaCRUD
OutputDir=installer
OutputBaseFilename=SistemaCRUD_Installer_2.0
Compression=lzma
SolidCompression=yes
AllowNoIcons=yes
DisableDirPage=no
DisableProgramGroupPage=no
DisableStartupPrompt=yes
UninstallDisplayIcon={app}\SistemaCRUD.exe
CreateUninstallRegKey=yes
UsePreviousAppDir=yes

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Files]
Source: "dist\SistemaCRUD.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\logo.ico"; DestDir: "{app}\assets"; Flags: ignoreversion
Source: "dist\logo.png"; DestDir: "{app}\assets"; Flags: ignoreversion

[Icons]
Name: "{group}\SistemaCRUD"; Filename: "{app}\SistemaCRUD.exe"
Name: "{commondesktop}\SistemaCRUD"; Filename: "{app}\SistemaCRUD.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na área de trabalho"; GroupDescription: "Atalhos:"; Flags: unchecked

[UninstallDelete]
Type: filesandordirs; Name: "{app}\assets"

[Run]
Filename: "{app}\SistemaCRUD.exe"; Description: "Executar SistemaCRUD"; Flags: nowait postinstall skipifsilent
