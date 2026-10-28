@echo off
title VentureTwin Launcher
echo ========================================================
echo Launching VentureTwin: Backend (8000) and Frontend (5173)
echo ========================================================

start "VentureTwin Backend (FastAPI)" cmd /k "cd /d C:\Users\visha\Documents\venture twin original\VentureTwin-main\backend && .\.venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8000 --reload"

timeout /t 2 /nobreak >nul

start "VentureTwin Frontend (Vite)" cmd /k "cd /d C:\Users\visha\ven frontend && npm run dev"

echo.
echo Both services launched!
echo - Frontend: http://localhost:5173/
echo - Backend API: http://127.0.0.1:8000/api/v1/health
echo - API Docs (Swagger): http://127.0.0.1:8000/docs
echo.

