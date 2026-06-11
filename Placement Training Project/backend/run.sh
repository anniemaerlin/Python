#!/bin/bash

# Dynamic Pricing Engine - Start Script
# This script starts the FastAPI application with proper configuration

set -e

echo "======================================"
echo "Dynamic Pricing Engine - Backend"
echo "======================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating..."
    python -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate || . venv/Scripts/activate

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p logs
mkdir -p app/models
mkdir -p config

# Check for .env file
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found!"
    echo "Creating .env from template..."
    cp .env.example .env
    echo "Please edit .env with your configuration."
fi

echo ""
echo "======================================"
echo "Starting API Server"
echo "======================================"
echo ""
echo "API will be available at:"
echo "  http://localhost:8000"
echo ""
echo "Documentation:"
echo "  Swagger UI: http://localhost:8000/api/docs"
echo "  ReDoc: http://localhost:8000/api/redoc"
echo ""
echo "Press Ctrl+C to stop the server"
echo "======================================"
echo ""

# Start the application
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
