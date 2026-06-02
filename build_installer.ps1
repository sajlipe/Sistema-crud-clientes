# Build the executable and prepare the installer files for Windows.
# Execute this in the project root using PowerShell.

$python = $env:PYTHON_EXECUTABLE
if (-not $python) {
    $python = "python"
}

Write-Host "Cleaning previous build output..."
Remove-Item -Recurse -Force .\build, .\dist, .\main.spec -ErrorAction SilentlyContinue

Write-Host "Building executable with PyInstaller..."
& $python -m pyinstaller --clean --noconsole --onefile --name SistemaCRUD --icon assets\logo.ico --add-data "assets/logo.png;assets" --add-data "assets/logo.ico;assets" main.py

Write-Host "Executable build complete. Output in .\dist\SistemaCRUD.exe"
Write-Host "If you want to build the installer, compile installer.iss with Inno Setup"
