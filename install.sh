#!/bin/bash
# Installation script for Vanta Code
# This script creates a virtual environment and installs Vanta in development mode

echo "Installing Vanta Code..."

# Check if python3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed or not in PATH."
    echo "Please install Python 3.11 or later from https://python.org"
    echo "On macOS, you can use: brew install python"
    echo "On Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    echo "On Windows: Download from python.org and add to PATH"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment."
        exit 1
    fi
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install in development mode
echo "Installing Vanta Code..."
python -m pip install -e .

if [ $? -eq 0 ]; then
    echo "Vanta Code installed successfully!"
    echo "Use './run.sh' to run Vanta from this directory."
else
    echo "Installation failed. Please check the errors above."
    exit 1
fi