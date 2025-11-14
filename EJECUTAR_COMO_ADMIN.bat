@echo off
REM Script para configurar tareas programadas (requiere permisos de Administrador)

echo.
echo ========================================================================
echo           CONFIGURACION DE TAREAS AUTOMATICAS - EA FC 26 BOT
echo ========================================================================
echo.
echo  Este script configurara actualizaciones automaticas en:
echo    - 9:00 AM  (Actualizacion matutina)
echo    - 1:00 PM  (Actualizacion mediodia)
echo    - 10:00 PM (Actualizacion nocturna)
echo.
echo  IMPORTANTE: Necesita ejecutarse como Administrador
echo.
echo ========================================================================
echo.

REM Verificar si se esta ejecutando como Administrador
net session >nul 2>&1
if %errorLevel% == 0 (
    echo  Ejecutando como Administrador... OK
    echo.
    python setup_scheduled_tasks.py
    echo.
    pause
) else (
    echo  ERROR: No se esta ejecutando como Administrador
    echo.
    echo  Por favor:
    echo    1. Click derecho en este archivo
    echo    2. Seleccionar "Ejecutar como administrador"
    echo.
    pause
    exit /b 1
)
