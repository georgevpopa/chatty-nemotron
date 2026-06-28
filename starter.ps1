#requires -Version 5.1

$Host.UI.RawUI.WindowTitle = "Chatty Nemotron - Starter"
$PROJECT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $PROJECT_DIR

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   🤖 Chatty Nemotron - Pornire..." -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Activeaza venv
$VenvPath = Join-Path $PROJECT_DIR ".venv\Scripts\Activate.ps1"
if (Test-Path $VenvPath) {
    Write-Host "[✓] Activare virtual environment..." -ForegroundColor Green
    & $VenvPath
} else {
    Write-Host "[✗] Virtual environment negasit!" -ForegroundColor Red
    Write-Host "    Ruleaza mai intai: python -m venv .venv" -ForegroundColor Yellow
    Read-Host "Apasa Enter pentru iesire"
    exit 1
}

# Verifica dependente
try {
    $null = python -c "import streamlit, openai, dotenv" 2>$null
    Write-Host "[✓] Dependente verificate." -ForegroundColor Green
} catch {
    Write-Host "[!] Instalare dependente..." -ForegroundColor Yellow
    pip install streamlit openai python-dotenv
}

# Verifica .env
if (-not (Test-Path ".env")) {
    Write-Host "[!] Atentie: .env negasit!" -ForegroundColor Yellow
    Write-Host "    Configureaza cheile API in .env" -ForegroundColor Yellow
    Start-Sleep -Seconds 3
}

# Porneste Streamlit
Write-Host "[✓] Pornire Streamlit pe http://localhost:8880" -ForegroundColor Green
Write-Host "[i] Apasa Ctrl+C pentru oprire" -ForegroundColor Gray
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

try {
    streamlit run app\main.py --server.port=8880 --server.headless=true
} finally {
    Write-Host ""
    Write-Host "[i] Streamlit s-a oprit." -ForegroundColor Cyan
    Read-Host "Apasa Enter pentru inchidere"
}
