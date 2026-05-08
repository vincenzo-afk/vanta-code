#!/bin/bash
# Run script for Vanta Code
# This script runs Vanta from the current directory using the virtual environment

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Error: Virtual environment not found. Run './install.sh' first."
    exit 1
fi

# Run Vanta
./.venv/bin/python3 -m vanta.cli.app "$@"