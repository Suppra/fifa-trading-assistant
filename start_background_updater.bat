@echo off
REM Iniciar actualizador en segundo plano (sin ventana visible)
REM Este script inicia el actualizador automático que se ejecuta
REM a las 9 AM, 1 PM y 10 PM sin necesidad de tener la app abierta

echo.
echo ========================================================================
echo           INICIANDO ACTUALIZADOR EN SEGUNDO PLANO
echo ========================================================================
echo.
echo  Este servicio actualizara precios de FUTBIN automaticamente:
echo    - 9:00 AM  (Actualizacion matutina)
echo    - 1:00 PM  (Actualizacion mediodia)
echo    - 10:00 PM (Actualizacion nocturna)
echo.
echo  El proceso se ejecuta en segundo plano (sin ventana)
echo  100 paginas (~3000 jugadores) por actualizacion
echo.
echo ========================================================================
echo.

REM Usar pythonw.exe para ejecutar sin ventana
start /B pythonw background_updater.py

echo  Servicio iniciado correctamente!
echo.
echo  Para detenerlo:
echo    - Abrir Administrador de tareas
echo    - Buscar proceso "pythonw.exe"
echo    - Finalizar tarea
echo.
echo  Para ver el log:
echo    - Abrir: logs\background_updater.log
echo.
echo ========================================================================
echo.

pause
