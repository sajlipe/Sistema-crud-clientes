[Setup]
AppId={{2DE9C7F8-1D0E-4A3A-9E86-5C6E3B0B7F22}}
AppName=Sistema de Gerenciamento de Clientes e Pedidos
AppVersion=2.0
AppVerName=SistemaCRUD 2.0
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

[Code]
procedure DeleteOldInstall();
var
  OldDirs: array[0..4] of string;
  I: Integer;
begin
  OldDirs[0] := 'C:\SistemaCRUD';
  OldDirs[1] := 'C:\Sistema de Gerenciamento de Clientes';
  OldDirs[2] := ExpandConstant('{pf}\SistemaCRUD');
  OldDirs[3] := ExpandConstant('{pf}\Sistema de Gerenciamento de Clientes');
  OldDirs[4] := ExpandConstant('{commonpf}\SistemaCRUD');

  for I := 0 to GetArrayLength(OldDirs) - 1 do
  begin
    if (OldDirs[I] <> '') and DirExists(OldDirs[I]) and FileExists(OldDirs[I] + '\SistemaCRUD.exe') then
    begin
      DelTree(OldDirs[I], True, True, True);
    end;
  end;
end;

function InitializeSetup(): Boolean;
begin
  Result := True;
  DeleteOldInstall();
end;
