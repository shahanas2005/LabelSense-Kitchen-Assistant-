@echo off
setlocal

echo Starting LabelSense...

if not exist "backend\app\main.py" (
  echo Error: backend/app/main.py not found.
  pause
  exit /b 1
)

if not exist "frontend\package.json" (
  echo Error: frontend/package.json not found.
  pause
  exit /b 1
)

if not exist "backend\.venv\Scripts\activate.bat" (
  echo Warning: backend virtual environment not found. Please create it first.
 ) else (
  start "LabelSense Backend" cmd /k "cd /d "%~dp0backend" && .venv\Scripts\activate.bat && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
 )

start "LabelSense Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

ping -n 2 127.0.0.1 >nul
start "" "http://localhost:5173"

echo LabelSense has launched. Backend on http://localhost:8000 and frontend on http://localhost:5173
endlocal
