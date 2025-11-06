<# 
  setup.ps1 — Environment bootstrap for Plane Boarding Simulator (Windows)
  Usage:
    In the repo root, run:
      powershell -ExecutionPolicy Bypass -File .\setup.ps1
#>

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "==============================="
Write-Host "Plane Boarding Simulator Setup (Windows)"
Write-Host "==============================="
Write-Host ""

function Get-Python {
    $py = (Get-Command py -ErrorAction SilentlyContinue)
    if ($py) { return "py" }

    $python = (Get-Command python -ErrorAction SilentlyContinue)
    if ($python) { return "python" }

    $python3 = (Get-Command python3 -ErrorAction SilentlyContinue)
    if ($python3) { return "python3" }

    return $null
}

$PY = Get-Python
if (-not $PY) {
    Write-Host "Python 3.10+ not found. Please install Python from https://www.python.org/downloads/."
    exit 1
}

try {
    if ($PY -eq "py") {
        $ver = & $PY -3 -c "import sys; print('.'.join(map(str, sys.version_info[:3])))"
    } else {
        $ver = & $PY -c "import sys; print('.'.join(map(str, sys.version_info[:3])))"
    }
    Write-Host "Using Python via '$PY' (version $ver)"
} catch {
    Write-Host "Could not determine Python version, continuing..."
}

if (-not (Test-Path -Path ".\venv")) {
    Write-Host "Creating virtual environment in .\venv ..."
    if ($PY -eq "py") {
        & $PY -3 -m venv venv
    } else {
        & $PY -m venv venv
    }
} else {
    Write-Host "Virtual environment already exists. Skipping creation."
}

$activate = ".\venv\Scripts\Activate.ps1"
if (-not (Test-Path $activate)) {
    Write-Host "Could not find $activate. Venv creation may have failed."
    exit 1
}

Write-Host "Activating virtual environment ..."
. $activate

Write-Host "Upgrading pip ..."
python -m pip install --upgrade pip

if (Test-Path ".\requirements.txt") {
    Write-Host "Installing dependencies from requirements.txt ..."
    pip install -r requirements.txt
} else {
    Write-Host "No requirements.txt found. Skipping dependency installation."
}

Write-Host ""
Write-Host "Environment setup complete!"
Write-Host ""
Write-Host "To activate later in PowerShell:"
Write-Host "  .\venv\Scripts\Activate.ps1"
Write-Host ""
Write-Host "Quick test (copy/paste):"
Write-Host @"
  setx PYTHONPATH "$PWD\src" >$null
  python - <<'PY'
from simulation import SimConfig, run_once
from basic_strategies import back_to_front

cfg = SimConfig(num_rows=6, num_passengers=30, seed=42)
metrics, plane, passengers = run_once(
    cfg,
    boarding_strategy=back_to_front,
    save_frames=True,
    auto_make_gif=True,
    gif_duration=120,
    gif_scale=2,
)
print('Total ticks:', metrics.total_ticks)
PY
"@
Write-Host ""
Write-Host "==============================="
Write-Host "Setup complete and ready to simulate."
Write-Host "==============================="

