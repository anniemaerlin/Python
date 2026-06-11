@echo off

REM Dynamic Pricing Engine - Start Script for Windows
REM This script starts the FastAPI application with proper configuration

setlocal enabledelayedexpansion

echo ======================================
echo Dynamic Pricing Engine - Backend
echo ======================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Virtual environment not found. Creating...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo Installing dependencies...
pip install -r requirements.txt

REM Create necessary directories
echo Creating necessary directories...
if not exist "logs" mkdir logs
if not exist "app\models" mkdir app\models
if not exist "config" mkdir config

REM Check for .env file
if not exist ".env" (
    echo Warning: .env file not found!
    echo Creating .env from template...
    copy .env.example .env
    echo Please edit .env with your configuration.
)

echo.
echo ======================================
echo Starting API Server
echo ======================================
echo.
echo API will be available at:
echo   http://localhost:8000
echo.
echo Documentation:
echo   Swagger UI: http://localhost:8000/api/docs
echo   ReDoc: http://localhost:8000/api/redoc
echo.
echo Press Ctrl+C to stop the server
echo ======================================
echo.

REM Start the application
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
