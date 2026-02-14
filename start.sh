#!/bin/bash

# DermaLens Backend Startup Script

echo "🧴 Starting DermaLens Backend..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "✅ .env file created. Please update it with your credentials."
    exit 1
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
else
    echo "⚠️  Virtual environment not found!"
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Check if database is accessible
echo "🔍 Checking database connection..."
python -c "
from app.core.config import settings
print(f'Database URL: {settings.DATABASE_URL}')
" || exit 1

# Run migrations
echo "🔄 Running database migrations..."
alembic upgrade head

# Start the server
echo "🚀 Starting FastAPI server..."
echo "📍 API will be available at: http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/api/v1/docs"
echo ""
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
