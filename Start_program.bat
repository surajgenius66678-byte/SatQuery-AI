@echo off
setlocal EnableExtensions EnableDelayedExpansion

title SatQuery AI - Start

cd /d "%~dp0"

echo.
echo ============================================================
echo                    SATQUERY AI
echo ============================================================
echo.
echo Project: %CD%
echo.

REM ------------------------------------------------------------
REM Configuration
REM ------------------------------------------------------------
set "VENV_DIR=venv324"
set "PYTHON=%VENV_DIR%\Scripts\python.exe"
set "PIP=%VENV_DIR%\Scripts\pip.exe"

set "BACKEND_HOST=127.0.0.1"
set "BACKEND_PORT=8000"
set "FRONTEND_PORT=3000"

REM ------------------------------------------------------------
REM [1/5] Check virtual environment
REM ------------------------------------------------------------
echo [1/5] Checking virtual environment...

if not exist "%PYTHON%" (
    echo.
    echo ============================================================
    echo ERROR: venv324 was not found.
    echo ============================================================
    echo.
    echo Expected:
    echo %CD%\%VENV_DIR%\Scripts\python.exe
    echo.
    echo Run Setup.bat first.
    pause
    exit /b 1
)

echo Virtual environment found.
echo.

REM ------------------------------------------------------------
REM [2/5] Check PyTorch
REM ------------------------------------------------------------
echo [2/5] Checking PyTorch and GPU...
echo.

"%PYTHON%" -c "import torch; print('PyTorch:',torch.__version__); print('CUDA available:',torch.cuda.is_available()); print('Device:',torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"

if errorlevel 1 (
    echo.
    echo ============================================================
    echo ERROR: PyTorch failed to load.
    echo ============================================================
    echo.
    echo The venv324 PyTorch installation is not working.
    echo Run Setup.bat again only if this happens.
    pause
    exit /b 1
)

echo.
echo PyTorch check passed.
echo.

REM ------------------------------------------------------------
REM [3/5] Check SatQuery imports
REM ------------------------------------------------------------
echo [3/5] Checking SatQuery backend...

"%PYTHON%" -c "import backend.api.main; import backend.model_registry.inference; print('SatQuery backend imports: OK')"

if errorlevel 1 (
    echo.
    echo ============================================================
    echo ERROR: SatQuery backend import failed.
    echo ============================================================
    echo.
    pause
    exit /b 1
)

echo.
echo SatQuery backend check passed.
echo.

REM ------------------------------------------------------------
REM [4/5] Start backend
REM ------------------------------------------------------------
echo [4/5] Starting backend...
echo.
echo Backend:
echo http://%BACKEND_HOST%:%BACKEND_PORT%
echo.

start "SatQuery AI - Backend" cmd /k ""%PYTHON%" -m uvicorn backend.api.main:app --host %BACKEND_HOST% --port %BACKEND_PORT%"

REM Give backend a moment to start
timeout /t 3 /nobreak >nul

REM ------------------------------------------------------------
REM [5/5] Start frontend
REM ------------------------------------------------------------
echo [5/5] Starting frontend...
echo.
echo Frontend:
echo http://%BACKEND_HOST%:%FRONTEND_PORT%
echo.

start "SatQuery AI - Frontend" cmd /k ""%PYTHON%" -m http.server %FRONTEND_PORT% --directory frontend"

timeout /t 2 /nobreak >nul

REM ------------------------------------------------------------
REM Open browser
REM ------------------------------------------------------------
echo.
echo ============================================================
echo                    SATQUERY AI READY
echo ============================================================
echo.
echo Frontend : http://%BACKEND_HOST%:%FRONTEND_PORT%
echo Backend  : http://%BACKEND_HOST%:%BACKEND_PORT%
echo.
echo Two terminal windows were opened:
echo   1. SatQuery AI - Backend
echo   2. SatQuery AI - Frontend
echo.
echo ============================================================
echo.

start "" "http://%BACKEND_HOST%:%FRONTEND_PORT%"

echo Browser opened.
echo.
echo This window can now be closed.
timeout /t 5 /nobreak >nul

endlocal
exit /b 0