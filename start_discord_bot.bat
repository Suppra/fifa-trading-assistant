@echo off
REM Inicia el servicio de Discord en segundo plano
REM Este script se puede ejecutar manualmente o al inicio de Windows

echo.
echo ========================================================================
echo   INICIANDO SERVICIO DE DISCORD - EA FC 26 BOT
echo ========================================================================
echo.

REM Cambiar al directorio del proyecto
cd /d "%~dp0"

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no encontrado
    echo Por favor instala Python desde https://python.org
    pause
    exit /b 1
)

REM Iniciar servicio en segundo plano sin ventana
echo Iniciando servicio de Discord en segundo plano...
start /B pythonw start_discord_service.py

echo.
echo Servicio iniciado correctamente!
echo El bot de Discord ahora esta ejecutandose en segundo plano.
echo.
echo Para verificar el estado, revisa: logs\discord_service.log
echo.

timeout /t 3 >nul
