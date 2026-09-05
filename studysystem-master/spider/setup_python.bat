@echo off
chcp 65001 >nul
echo ================================
echo Python Auto Setup Script
echo ================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% == 0 (
    echo [OK] Python is installed
    python --version
    echo.
    goto :install_deps
)

echo [ERROR] Python not installed
echo.
echo Please install Python manually:
echo.
echo 1. Visit: https://www.python.org/downloads/
echo 2. Download Python 3.10 or higher
echo 3. Check "Add Python to PATH" during installation
echo 4. Click "Install Now"
echo 5. Run this script again after installation
echo.
pause
exit /b 1

:install_deps
echo ================================
echo Installing Dependencies
echo ================================
echo.

cd /d %~dp0

pip install -r requirements.txt
if %errorlevel% == 0 (
    echo.
    echo [OK] Dependencies installed successfully
    echo.
    echo ================================
    echo Setup Complete!
    echo ================================
    echo.
    echo Run all spiders:
    echo   python run_all_spiders.py
    echo.
    echo Run Bilibili spider:
    echo   python run_all_spiders.py --bili
    echo.
) else (
    echo.
    echo [ERROR] Failed to install dependencies
    echo.
)

pause
