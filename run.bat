@echo off
REM Run script for Vanta Code (Windows)
REM This script runs Vanta from the current directory

REM Check if python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: python is not installed or not in PATH.
    echo Please install Python 3.11 or later.
    pause
    exit /b 1
)

REM Run Vanta with all arguments
python -m vanta %*