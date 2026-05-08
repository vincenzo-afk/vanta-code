@echo off
REM Installation script for Vanta Code (Windows)
REM This script installs Vanta in development mode using pip

echo Installing Vanta Code...

REM Check if python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: python is not installed or not in PATH.
    echo Please install Python 3.11 or later from https://python.org
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

REM Check if pip is available
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo Error: pip is not available.
    echo Please ensure pip is installed with Python.
    pause
    exit /b 1
)

REM Install in development mode
python -m pip install -e .

if %errorlevel% equ 0 (
    echo Vanta Code installed successfully!
    echo You can now run 'vanta' from the command prompt, or use 'run.bat' from this directory.
) else (
    echo Installation failed. Please check the errors above.
    pause
    exit /b 1
)

pause