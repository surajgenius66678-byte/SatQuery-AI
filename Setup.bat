@echo off
setlocal EnableExtensions EnableDelayedExpansion

title SatQuery AI - Automatic Setup

cd /d "%~dp0"

echo.
echo ============================================================
echo                 SATQUERY AI SETUP
echo ============================================================
echo.

REM ------------------------------------------------------------
REM Check Python
REM ------------------------------------------------------------
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Install Python 3.12 and run Setup.bat again.
    pause
    exit /b 1
)

echo [OK] Python detected:
python --version
echo.

REM ------------------------------------------------------------
REM Virtual environment: venv324
REM ------------------------------------------------------------
set "VENV_DIR=venv324"
set "PYTHON=%VENV_DIR%\Scripts\python.exe"
set "PIP=%VENV_DIR%\Scripts\pip.exe"

if not exist "%PYTHON%" (
    echo [INFO] Creating virtual environment: %VENV_DIR%
    python -m venv "%VENV_DIR%"

    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

echo [OK] Virtual environment ready: %VENV_DIR%
echo.

REM ------------------------------------------------------------
REM Verify virtual environment Python
REM ------------------------------------------------------------
echo [INFO] Using Python:
"%PYTHON%" --version
echo.

REM ------------------------------------------------------------
REM Upgrade pip
REM ------------------------------------------------------------
echo [INFO] Upgrading pip...
"%PYTHON%" -m pip install --upgrade pip

if errorlevel 1 (
    echo [ERROR] Failed to upgrade pip.
    pause
    exit /b 1
)

echo.

REM ------------------------------------------------------------
REM Detect NVIDIA GPU
REM ------------------------------------------------------------
where nvidia-smi >nul 2>&1

if errorlevel 1 (
    echo ============================================================
    echo                 CPU-ONLY SYSTEM DETECTED
    echo ============================================================
    echo.
    echo Installing CPU-only PyTorch...
    echo.

    "%PYTHON%" -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

    if errorlevel 1 (
        echo.
        echo [ERROR] CPU PyTorch installation failed.
        pause
        exit /b 1
    )

    set "TORCH_MODE=CPU"

) else (
    echo ============================================================
    echo                 NVIDIA GPU DETECTED
    echo ============================================================
    echo.

    echo NVIDIA information:
    nvidia-smi
    echo.

    echo [INFO] Installing CUDA-enabled PyTorch...
    echo.

    "%PYTHON%" -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128

    if errorlevel 1 (
        echo.
        echo [ERROR] CUDA PyTorch installation failed.
        pause
        exit /b 1
    )

    set "TORCH_MODE=CUDA"
)

echo.
echo ============================================================
echo              PYTORCH INSTALLATION COMPLETE
echo ============================================================
echo.

REM ------------------------------------------------------------
REM Install remaining SatQuery dependencies
REM ------------------------------------------------------------
echo [INFO] Installing SatQuery dependencies...
echo.

"%PYTHON%" -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo [ERROR] Dependency installation failed.
    pause
    exit /b 1
)

REM ------------------------------------------------------------
REM Verify PyTorch
REM ------------------------------------------------------------
echo.
echo ============================================================
echo                 VERIFYING PYTORCH
echo ============================================================
echo.

"%PYTHON%" -c "import torch; print('PyTorch:', torch.__version__); print('CUDA build:', torch.version.cuda); print('CUDA available:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"

if errorlevel 1 (
    echo.
    echo [ERROR] PyTorch verification failed.
    pause
    exit /b 1
)

REM ------------------------------------------------------------
REM Preflight
REM ------------------------------------------------------------
echo.
echo ============================================================
echo                 RUNNING SATQUERY PREFLIGHT
echo ============================================================
echo.

if exist "scripts\preflight_real.py" (
    "%PYTHON%" scripts\preflight_real.py
)

echo.
echo ============================================================
echo                    SETUP COMPLETE
echo ============================================================
echo.
echo Virtual environment: %VENV_DIR%
echo PyTorch mode: %TORCH_MODE%
echo.
echo NOTE:
echo Real Qwen2-VL, Grounding DINO and CROMA inference
echo require substantial RAM/VRAM. CPU systems can run
echo the application architecture and lightweight tests,
echo but real model inference may be very slow or impractical.
echo.
pause