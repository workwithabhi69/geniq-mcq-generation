@echo off
echo ========================================================
echo   Starting GENIQ: GenAI Automatic MCQ Generation System
echo ========================================================
echo.

echo [1/2] Launching FastAPI Backend on http://127.0.0.1:8000 ...
start "GENIQ Backend" cmd /k "cd backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

timeout /t 3 /nobreak >nul

echo [2/2] Launching React Vite Frontend on http://localhost:5173 ...
start "GENIQ Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================================
echo   GENIQ is running!
echo   - Frontend: http://localhost:5173
echo   - Backend API: http://127.0.0.1:8000/docs
echo ========================================================
echo.
pause
