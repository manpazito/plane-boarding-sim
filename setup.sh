#!/usr/bin/env bash
# setup.sh — Environment bootstrap for Plane Boarding Simulator
# Usage: bash setup.sh
# (Optional) You can also run this with: chmod +x setup.sh && ./setup.sh

set -e  # Exit on first error

echo ""
echo "==============================="
echo "Plane Boarding Simulator Setup"
echo "==============================="
echo ""

# Detect Python version
PYTHON_CMD=$(command -v python3 || command -v python)
if [ -z "$PYTHON_CMD" ]; then
  echo "Python is not installed. Please install Python 3.10+ first."
  exit 1
fi

echo "Using Python at: $PYTHON_CMD"
PY_VERSION=$($PYTHON_CMD -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')
echo "Detected Python version: $PY_VERSION"
echo ""

# Create a virtual environment
if [ ! -d "venv" ]; then
  echo "Creating virtual environment in ./venv ..."
  $PYTHON_CMD -m venv venv
else
  echo "Virtual environment already exists. Skipping creation."
fi

# Activate environment
echo ""
echo "Activating virtual environment ..."
source venv/bin/activate

# Upgrade pip and install dependencies
echo ""
echo "Upgrading pip ..."
pip install --upgrade pip

if [ -f "requirements.txt" ]; then
  echo "Installing dependencies from requirements.txt ..."
  pip install -r requirements.txt
else
  echo "No requirements.txt found. Skipping dependency installation."
fi

# Confirmation
echo ""
echo "Environment setup complete!"
echo ""
echo "To activate your environment later, run:"
echo "  source venv/bin/activate"
echo ""
echo "To test the simulator quickly, try:"
echo ""
echo "  PYTHONPATH=src python3 - <<'PY'"
echo "  from simulation import SimConfig, run_once"
echo "  from basic_strategies import back_to_front"
echo "  cfg = SimConfig(num_rows=6, num_passengers=30, seed=42)"
echo "  metrics, plane, passengers = run_once(cfg, boarding_strategy=back_to_front, save_frames=True, auto_make_gif=True)"
echo "  print('Total ticks:', metrics.total_ticks)"
echo "  PY"
echo ""
echo "==============================="
echo "Ready to simulate!"
echo "==============================="
