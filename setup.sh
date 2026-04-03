#!/bin/bash
# Instagram Backend — Quick Setup Script

set -e

echo "================================"
echo " Instagram Backend Setup"
echo "================================"

# Check Python
python3 --version || { echo "Python 3 required"; exit 1; }

# Create virtualenv
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate
source venv/bin/activate

# Install deps
echo "Installing dependencies..."
pip install -r requirements.txt -q

# Check .env
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  .env file not found!"
    echo "Copy .env.example to .env and fill in your Supabase credentials:"
    echo ""
    echo "  cp .env.example .env"
    echo "  nano .env"
    echo ""
    exit 1
fi

# Run migrations
echo "Running migrations..."
python manage.py migrate

echo ""
echo "✅ Setup complete!"
echo ""
echo "Start server:"
echo "  source venv/bin/activate"
echo "  python manage.py runserver"
echo ""
echo "API: http://localhost:8000/api/"
echo "Admin: http://localhost:8000/admin/"
