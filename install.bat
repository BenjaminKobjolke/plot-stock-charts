@echo off
echo Installing Remember The Milk Exporter...

REM Check if Python is installed
call python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in the PATH.
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if Git is installed (needed for pip install from GitHub)
call git --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Git is not installed or not in the PATH.
    echo Please install Git from https://git-scm.com/downloads
    echo It is required to install packages from GitHub.
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist venv (
    echo Creating virtual environment...
    call python -m venv venv
)

REM Activate virtual environment and install dependencies
echo Activating virtual environment...
call %~dp0\venv\Scripts\activate.bat

echo Installing pip and setuptools...
call pip install --upgrade pip setuptools wheel

echo Installing dependencies (including rtmilk from GitHub)...
call pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo Error installing dependencies.
    echo Please check your internet connection and try again.
    pause
    exit /b 1
)

echo.
echo Installation completed successfully!
echo.
echo Please edit settings.ini to add your Remember The Milk API credentials.
echo.
pause
