@echo off
set PROJECT_DIR=%~dp0
set SERVER_DIR=%PROJECT_DIR%server
set CLIENT_DIR=%PROJECT_DIR%client

echo [0/4] Ensuring Redis is running in WSL (Ubuntu)...
wsl -d Ubuntu -u root service redis-server start

echo [1/4] Starting FastAPI Backend...
start cmd /k "cd /d %SERVER_DIR% && venv\Scripts\activate && uvicorn app.main:app --reload --port 8000"

echo [2/4] Starting Celery Worker (Executor Agent)...
start cmd /k "cd /d %SERVER_DIR% && venv\Scripts\activate && celery -A app.core.celery_app worker -P solo --loglevel=info"

echo [3/4] Starting Celery Beat (Scheduler)...
start cmd /k "cd /d %SERVER_DIR% && venv\Scripts\activate && celery -A app.core.celery_app beat --loglevel=info"

echo [4/4] Starting Frontend (Port 8080)...
start cmd /k "cd /d %CLIENT_DIR% && npm run dev"


pause
