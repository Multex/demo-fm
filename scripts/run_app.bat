@echo off
setlocal
title Demo FM - Iniciando...

echo Verificando instalacion de Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python no se encuentra instalado o no esta en el PATH.
    echo Por favor instale Python desde python.org y asegurese de marcar "Add Python to PATH".
    echo.
    pause
    exit /b 1
)

echo.
echo Instalando/Verificando librerias necesarias...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Hubo un problema instalando las librerias.
    echo Verifique su conexion a internet.
    pause
    exit /b 1
)

echo.
echo Iniciando la aplicacion...
echo Se abrira en su navegador predeterminado.
cd /d "%~dp0\.." && python -m streamlit run src\fm_demo_streamlit.py

if %errorlevel% neq 0 (
    echo.
    echo La aplicacion se cerro inesperadamente.
    pause
)
