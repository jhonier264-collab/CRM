@echo off
setlocal
title CRM Ecosystem Launcher

:: ── Leer puertos desde .env (con valores por defecto) ──────────────────────
set "BACKEND_PORT=8000"
set "FRONTEND_PORT=3000"

if exist "%~dp0.env" (
    for /f "usebackq tokens=1,* delims==" %%A in ("%~dp0.env") do (
        set "line=%%A"
        if /i "%%A"=="BACKEND_PORT"  set "BACKEND_PORT=%%B"
        if /i "%%A"=="FRONTEND_PORT" set "FRONTEND_PORT=%%B"
    )
)
:: ───────────────────────────────────────────────────────────────────────────

echo ========================================================
echo       Iniciando Ecosistema CRM SaaS Modular...
echo ========================================================
echo   Backend  : http://localhost:%BACKEND_PORT%
echo   Frontend : http://localhost:%FRONTEND_PORT%
echo ========================================================
echo.

:: 1. CHECK MYSQL SERVICE
echo [1/4] Verificando servicio de Base de Datos (MySQL)...
sc query "MySQL80" | find "RUNNING" >nul
if %errorlevel% neq 0 (
    echo    MySQL no esta corriendo. Intentando iniciar...
    net start MySQL80
    if %errorlevel% neq 0 (
        echo    [!] ADVERTENCIA: No se pudo iniciar MySQL. Asegurate de que el servicio 'MySQL80' exista o inicie manualmente.
        pause
    ) else (
        echo    MySQL iniciado correctamente.
    )
) else (
    echo    MySQL ya esta corriendo.
)
echo.

:: 2. START BACKEND
echo [2/4] Iniciando Backend en puerto %BACKEND_PORT%...
start "CRM Backend (Puerto %BACKEND_PORT%)" /D "%~dp0backend" cmd /k "color 0A && echo Iniciando Backend en puerto %BACKEND_PORT%... && if exist venv\Scripts\activate.bat (call venv\Scripts\activate.bat && echo VirtualEnv Activado) else (echo No se detecto venv, usando Python global) && python api_server.py"
echo    Backend lanzado en nueva ventana (Verde).
echo.

:: 3. START FRONTEND
echo [3/4] Iniciando Frontend en puerto %FRONTEND_PORT%...
start "CRM Frontend (Puerto %FRONTEND_PORT%)" /D "%~dp0frontend" cmd /k "color 09 && echo Iniciando Frontend en puerto %FRONTEND_PORT%... && npm run dev"
echo    Frontend lanzado en nueva ventana (Azul).
echo.

:: 4. OPEN BROWSER
echo [4/4] Abriendo navegador en 5 segundos...
timeout /t 5 >nul
start "" "http://localhost:%FRONTEND_PORT%"

echo.
echo ========================================================
echo       Ecosistema Iniciado. Minimice esta ventana.
echo ========================================================
echo.
pause
