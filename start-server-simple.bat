@echo off
cd /d "C:\Users\Pc\Desktop\clinicflow-ai\backend"
call .\venv\Scripts\activate.bat
echo ==========================================
echo   Démarrage du Backend DermaFlow AI
echo ==========================================
echo Serveur: http://localhost:8000
echo Docs:   http://localhost:8000/docs
echo ==========================================
start http://localhost:8000/docs
uvicorn main:app --reload --host 0.0.0.0 --port 8000
pause
