# Iniciar Xolix 3.0 — Backend + Frontend en paralelo
Write-Host "=== XOLIX 3.0 — Inicio ===" -ForegroundColor Cyan
Write-Host ""

# Backend
Write-Host "[1/2] Iniciando backend FastAPI en http://localhost:8000 ..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", @"
cd '$PSScriptRoot'
Write-Host 'Backend - FastAPI' -ForegroundColor Green
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload
"@

Start-Sleep -Seconds 2

# Frontend
Write-Host "[2/2] Iniciando frontend React en http://localhost:5173 ..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", @"
cd '$PSScriptRoot\frontend'
Write-Host 'Frontend - Vite/React' -ForegroundColor Green
npm run dev
"@

Write-Host ""
Write-Host "Ambos servicios iniciados." -ForegroundColor Green
Write-Host "  Backend:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "  Docs API: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "  Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host ""
Write-Host "Credenciales demo:" -ForegroundColor White
Write-Host "  director@xolix.com      | admin123"
Write-Host "  coordinador@xolix.com   | coord123"
Write-Host "  psicologa@xolix.com     | psico123"
Write-Host "  trabajo_social@xolix.com| social123"
Write-Host "  legal@xolix.com         | legal123"
