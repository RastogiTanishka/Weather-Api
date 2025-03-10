$APP_DIR = Split-Path -Parent $MyInvocation.MyCommand.Definition
$VENV_DIR = "$APP_DIR\venv"
$EXECUTABLE = "$APP_DIR\run.ps1"

Write-Host "Setting up virtual environment..."
python -m venv $VENV_DIR

Write-Host "Activating virtual environment and installing dependencies..."
& "$VENV_DIR\Scripts\Activate"
pip install --upgrade pip
pip install flask requests psycopg2-binary

Write-Host "Creating run executable..."
Set-Content -Path $EXECUTABLE -Value @"
& `"$VENV_DIR\Scripts\Activate`"
python app.py
"@

Write-Host "Setup complete. Run '.\run.ps1' to start the API."

