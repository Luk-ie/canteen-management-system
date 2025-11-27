@echo off
title Canteen Management System
echo Starting Canteen Management System...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher from https://python.org
    pause
    exit /b 1
)

REM Install requirements
echo Installing required packages...
pip install -r requirements.txt

REM Create necessary directories
if not exist "data" mkdir data
if not exist "config" mkdir config
if not exist "backups" mkdir backups
if not exist "reports" mkdir reports

REM Start the application
echo Starting Streamlit application...
streamlit run app.py

pause