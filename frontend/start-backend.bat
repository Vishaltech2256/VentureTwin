@echo off
title VentureTwin - Backend Server
echo ===================================================
echo Starting VentureTwin Backend (FastAPI on Port 8000)
echo ===================================================
cd /d "C:\Users\visha\Documents\venture twin original\VentureTwin-main\backend"
".\.venv\Scripts\uvicorn.exe" app.main:app --host 127.0.0.1 --port 8000 --reload
pause

