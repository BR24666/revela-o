@echo off
echo ========================================
echo   SUPER ANALISTA - REALTIME ENGINE
echo ========================================
echo.

cd /d %~dp0

REM Ativar ambiente virtual
if exist ..\venv\Scripts\activate.bat (
    call ..\venv\Scripts\activate.bat
) else (
    echo ERRO: Ambiente virtual nao encontrado!
    echo Execute: python -m venv venv
    pause
    exit /b 1
)

echo Iniciando engine de tempo real...
echo.

python realtime_engine.py

pause

