#!/bin/bash

echo "🎬 Setting up A24 Style Transfer App..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    exit 1
fi

# Backend setup
echo "🐍 Setting up backend..."
cd backend

# Create virtual environment
python3 -m venv venv
echo "✅ Virtual environment created"

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi
echo "✅ Virtual environment activated"

# Install Python dependencies
pip install -r requirements.txt
echo "✅ Python dependencies installed"

cd ..

# Frontend setup
echo "⚛️ Setting up frontend..."
cd frontend

# Install Node.js dependencies
npm install
echo "✅ Node.js dependencies installed"

cd ..

# Create sample asset directories
echo "📁 Creating asset directories..."
mkdir -p backend/assets/luts
mkdir -p backend/assets/grain_textures
mkdir -p backend/assets/models

echo "🎉 Setup complete!"
echo ""
echo "🚀 To start development:"
echo ""
echo "Backend (Terminal 1):"
echo "  cd backend"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "  venv\\Scripts\\activate"
else
    echo "  source venv/bin/activate"
fi
echo "  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "Frontend (Terminal 2):"
echo "  cd frontend"
echo "  npm start"
echo ""
echo "🐳 Or use Docker:"
echo "  docker-compose up --build"
echo ""
echo "📖 Access the app:"
echo "  Frontend: http://localhost:3000"
echo "  Backend API: http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"