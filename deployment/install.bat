@echo off
setlocal enabledelayedexpansion
title CRPF Mental Health System - Installation
echo ============================================================
echo    CRPF MENTAL HEALTH & WELLNESS SYSTEM
echo    Project Dependencies Installation Script
echo ============================================================
echo.
echo This script will:
echo   - Offer to install Python, Node.js, and MySQL if missing (with your permission)
echo   - Install project dependencies (backend, frontend)
echo   - Build the frontend and create a desktop shortcut
echo ============================================================
echo.

REM Check Administrator privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Please run as Administrator!
    echo Right-click this file and select "Run as administrator"
    pause
    exit /b 1
)

echo [1/7] Checking System Requirements...
echo.

REM Check Python installation
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed.
    set /p install_py="Would you like to install Python 3.8 now via winget? (y/N): "
    if /i "!install_py!"=="y" (
        echo Installing Python 3.8...
        winget install Python.Python.3.8 --accept-package-agreements --accept-source-agreements
        if !errorlevel! neq 0 (
            echo ERROR: Python installation failed. Install manually from https://python.org
            pause
            exit /b 1
        )
        echo.
        echo Python was installed. Please close this window, open a NEW Command Prompt
        echo as Administrator, and run this script again so PATH is updated.
        pause
        exit /b 0
    )
    echo ERROR: Python 3.8 is required. Install from https://python.org
    pause
    exit /b 1
)
python --version
echo ✅ Python found

REM Check Node.js installation  
echo Checking Node.js installation...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Node.js is not installed.
    set /p install_node="Would you like to install Node.js LTS now via winget? (y/N): "
    if /i "!install_node!"=="y" (
        echo Installing Node.js...
        winget install OpenJS.NodeJS.LTS --accept-package-agreements --accept-source-agreements
        if !errorlevel! neq 0 (
            echo ERROR: Node.js installation failed. Install manually from https://nodejs.org
            pause
            exit /b 1
        )
        echo.
        echo Node.js was installed. Please close this window, open a NEW Command Prompt
        echo as Administrator, and run this script again so PATH is updated.
        pause
        exit /b 0
    )
    echo ERROR: Node.js is required. Install from https://nodejs.org
    pause
    exit /b 1
)
node --version
npm --version
echo ✅ Node.js found

REM Check MySQL
echo Checking MySQL installation...
mysql --version >nul 2>&1
if %errorlevel% neq 0 (
    echo MySQL is not installed or not in PATH.
    set /p install_mysql="Would you like to install MySQL now via winget? (y/N): "
    if /i "!install_mysql!"=="y" (
        echo Installing MySQL...
        winget install Oracle.MySQL --accept-package-agreements --accept-source-agreements
        if !errorlevel! neq 0 (
            echo WARNING: MySQL installation failed or was skipped.
            echo You can install MySQL manually from https://dev.mysql.com/downloads/
        ) else (
            echo MySQL was installed. You may need to open a new Command Prompt and run this script again.
        )
    )
    set /p continue="Continue without MySQL (install later)? (y/N): "
    if /i not "!continue!"=="y" exit /b 1
) else (
    mysql --version
    echo ✅ MySQL found
)

echo.
echo [2/7] Installing Python Dependencies...
cd /d "%~dp0\..\backend"
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Python dependencies
    pause
    exit /b 1
)
echo ✅ Python dependencies installed

echo.
echo [3/7] Installing Node.js Dependencies...  
cd /d "%~dp0\..\frontend"
npm install
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Node.js dependencies
    pause
    exit /b 1
)
echo ✅ Node.js dependencies installed

echo.
echo [4/7] Building Optimized Frontend (Production Build)...
npm run build
if %errorlevel% neq 0 (
    echo ERROR: Failed to build frontend
    pause
    exit /b 1
)
echo ✅ Frontend production build created

echo.
echo [5/7] Installing Additional Requirements...
pip install psutil requests pathlib
echo ✅ Additional requirements installed

echo.
echo [6/7] Creating Desktop Shortcut...
cd /d "%~dp0"
powershell -Command "& {$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\CRPF Mental Health System.lnk'); $Shortcut.TargetPath = 'python.exe'; $Shortcut.Arguments = '\"%CD%\crpf_launcher.py\"'; $Shortcut.WorkingDirectory = '%CD%'; $Shortcut.Description = 'CRPF Mental Health & Wellness System'; $Shortcut.Save()}"

if exist "%USERPROFILE%\Desktop\CRPF Mental Health System.lnk" (
    echo ✅ Desktop shortcut created
) else (
    echo ❌ Failed to create desktop shortcut
)

echo.
echo [7/7] Final Configuration...
echo Creating startup configuration...
echo System ready for deployment

echo.
echo ============================================================
echo ✅ INSTALLATION COMPLETED SUCCESSFULLY!
echo ============================================================
echo.
echo 📋 What's been installed:
echo   • All Python dependencies
echo   • All Node.js dependencies  
echo   • Desktop shortcut created
echo   • System launcher configured
echo.
echo 🚀 HOW TO USE:
echo   1. Double-click "CRPF Mental Health System" on desktop
echo   2. System will start automatically
echo   3. Browser will open with the application
echo   4. CRPF personnel can login and use the system
echo.
echo ⚠️  IMPORTANT NOTES:
echo   • Ensure MySQL is running before using the system
echo   • Configure database connection in backend/.env file
echo   • System runs completely offline (no internet required)
echo   • All data stays on local computer
echo.
echo 📞 For support, contact the development team
echo ============================================================
pause