@echo off
echo ========================================
echo   SUPER ANALISTA - TREINAMENTO ML
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

echo Iniciando treinamento do modelo...
echo AVISO: Este processo pode levar de 10 a 60 minutos!
echo.

python ml_model.py

echo.
echo ========================================
echo   TREINAMENTO CONCLUIDO!
echo ========================================
pause

