#!/bin/bash
# Qiskit Environment Setup Script

echo "Setting up Qiskit virtual environment..."

# Create virtual environment
python -m venv qiskit_venv

# Activate virtual environment
source qiskit_venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install required packages
pip install -r requirements.txt

echo "Virtual environment setup complete!"
echo "To activate the environment, run:"
echo "source qiskit_venv/bin/activate"
echo ""
echo "To deactivate the environment, run:"
echo "deactivate"