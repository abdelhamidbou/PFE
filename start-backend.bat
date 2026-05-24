@echo off
chcp 65001 >nul
echo ==========================================
echo   DermaFlow AI Backend Starter
echo ==========================================
echo.
cd /d "C:\Users\Pc\Desktop\clinicflow-ai\backend"
echo Activating virtual environment...
call .\venv\Scripts\activate.bat
echo.
echo Starting backend server...
echo Server will be available at: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo ==========================================
uvicorn main:app --reload --host 0.0.0.0 --port 8000
