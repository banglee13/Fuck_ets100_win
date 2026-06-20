@echo off
cd /d "%~dp0"

echo ========================================
echo    Fuck ETS100 - Windows Version
echo ========================================
echo.

echo [1/3] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found, please install Python 3.8+
    pause
    exit /b 1
)

echo [2/3] Installing dependencies...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

echo.
echo [3/3] Starting program...
echo.
python main.py

if errorlevel 1 (
    echo.
    echo Program exited with error
    pause
)
