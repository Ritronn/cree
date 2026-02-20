#!/bin/bash

# Setup script for Eisenhower Matrix Task Management System

echo "=== Eisenhower Matrix Task Management Setup ==="
echo ""

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed"
    exit 1
fi

if ! command -v psql &> /dev/null; then
    echo "Warning: PostgreSQL client not found. Make sure PostgreSQL is installed."
fi

echo "Prerequisites check passed!"
echo ""

# Backend setup
echo "=== Setting up Backend ==="
cd backend

echo "Creating virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Copying environment file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file. Please edit it with your configuration."
fi

echo ""
echo "To complete backend setup, run:"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  python manage.py makemigrations"
echo "  python manage.py migrate"
echo "  python manage.py createsuperuser"
echo "  python manage.py runserver"
echo ""

cd ..

# Frontend setup
echo "=== Setting up Frontend ==="
cd frontend

echo "Installing Node dependencies..."
npm install

echo "Copying environment file..."
if [ ! -f .env ]; then
    cp .env.example .env
fi

echo ""
echo "To start frontend, run:"
echo "  cd frontend"
echo "  npm run dev"
echo ""

cd ..

echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Configure backend/.env with your database and API credentials"
echo "2. Create PostgreSQL database: createdb eisenhower_matrix"
echo "3. Run backend migrations (see commands above)"
echo "4. Start backend server: cd backend && python manage.py runserver"
echo "5. Start frontend server: cd frontend && npm run dev"
echo "6. (Optional) Start Celery worker: cd backend && celery -A eisenhower_matrix worker -l info"
