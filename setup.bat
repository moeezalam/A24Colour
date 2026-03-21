@echo off
echo 🎬 Setting up A24 Style Transfer App...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 3 is required but not installed.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is required but not installed.
    pause
    exit /b 1
)

REM Backend setup
echo 🐍 Setting up backend...
cd backend

REM Create virtual environment
python -m venv venv
echo ✅ Virtual environment created

REM Activate virtual environment
call venv\Scripts\activate
echo ✅ Virtual environment activated

REM Install Python dependencies
pip install -r requirements.txt
echo ✅ Python dependencies installed

cd ..

REM Frontend setup
echo ⚛️ Setting up frontend...
cd frontend

REM Install Node.js dependencies
npm install
echo ✅ Node.js dependencies installed

cd ..

REM Create sample asset directories
echo 📁 Creating asset directories...
if not exist "backend\assets\luts" mkdir backend\assets\luts
if not exist "backend\assets\grain_textures" mkdir backend\assets\grain_textures
if not exist "backend\assets\models" mkdir backend\assets\models

echo 🎉 Setup complete!
echo.
echo 🚀 To start development:
echo.
echo Backend (Terminal 1):
echo   cd backend
echo   venv\Scripts\activate
echo   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
echo.
echo Frontend (Terminal 2):
echo   cd frontend
echo   npm start
echo.
echo 🐳 Or use Docker:
echo   docker-compose up --build
echo.
echo 📖 Access the app:
echo   Frontend: http://localhost:3000
echo   Backend API: http://localhost:8000
echo   API Docs: http://localhost:8000/docs

pause