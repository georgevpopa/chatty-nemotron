@echo off
title Chatty Nemotron - Clear Cache
color 0B

echo ==========================================
echo    🧹 Chatty Nemotron - Curatare Cache
echo ==========================================
echo.

set "PROJECT_DIR=%~dp0"
cd /d "!PROJECT_DIR!"

echo [i] Stergere cache Python...

:: Sterge __pycache__ recursiv
for /d /r . %%d in (__pycache__) do (
    if exist "%%d" (
        echo     [DEL] %%d
        rmdir /s /q "%%d"
    )
)

:: Sterge fisiere .pyc
for /r . %%f in (*.pyc) do (
    if exist "%%f" (
        echo     [DEL] %%f
        del /q "%%f"
    )
)

echo.
echo [OK] Cache curatat!
echo [i] Poti acum reporni starter.bat
echo.

pause
