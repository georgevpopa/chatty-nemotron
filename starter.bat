@echo off
setlocal enabledelayedexpansion

set "PROJECT_DIR=%~dp0"
cd /d "!PROJECT_DIR!"
set "VENV_PYTHON=!PROJECT_DIR!.venv\Scripts\python.exe"
set "VENV_STREAMLIT=!PROJECT_DIR!.venv\Scripts\streamlit.exe"

:: Verifica venv
if not exist "!VENV_PYTHON!" (
    echo [EROARE] Virtual environment negasit.
    echo Ruleaza: python -m venv .venv
    pause
    exit /b 1
)

:: Verifica dependente
"!VENV_PYTHON!" -c "import streamlit, openai, dotenv" >nul 2>&1
if errorlevel 1 (
    echo [!] Instalare dependente...
    "!PROJECT_DIR!.venv\Scripts\pip.exe" install streamlit openai python-dotenv
)

:: Verifica fisiere
if not exist "!PROJECT_DIR!app\main.py" (
    echo [EROARE] app\main.py negasit!
    pause
    exit /b 1
)

:: Porneste Streamlit IN BACKGROUND
echo [i] Pornire Streamlit pe port 8880...
start "Chatty Streamlit" "!VENV_STREAMLIT!" run app\main.py --server.port=8880 --server.headless=true

:: Asteapta 4 secunde sa porneasca serverul
echo [i] Astept pornire server...
timeout /t 4 /nobreak >nul

:: Deschide browserul automat
echo [i] Deschid browser...
start http://localhost:8880

:: Gata - inchide fereastra CMD
echo [OK] Chatty Nemotron ruleaza. Poti inchide aceasta fereastra.
timeout /t 2 >nul
exit