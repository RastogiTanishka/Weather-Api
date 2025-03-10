$APP_DIR = Split-Path -Parent $MyInvocation.MyCommand.Definition
$VENV_DIR = "$APP_DIR\venv"

# Ensure the virtual environment exists
if (!(Test-Path "$VENV_DIR")) {
    Write-Host "Virtual environment not found. Run .\setup.ps1 first."
    exit 1
}

# Activate the virtual environment and run the app
& "$VENV_DIR\Scripts\Activate"
python "$APP_DIR\app.py"

