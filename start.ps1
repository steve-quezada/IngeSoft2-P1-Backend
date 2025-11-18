# Script para ejecutar la aplicación completa en local con un solo comando
# Ejecutar desde: Proyecto Back/

Write-Host "=== Iniciando Aplicación Completa ===" -ForegroundColor Cyan
Write-Host ""

# Verificar PostgreSQL
Write-Host "Verificando PostgreSQL..." -ForegroundColor Yellow
$pgStatus = docker ps --filter "name=postgres-db" --format "{{.Status}}"
if (-not $pgStatus) {
    Write-Host "Iniciando PostgreSQL..." -ForegroundColor Yellow
    Set-Location "docker"
    docker-compose up -d postgres
    Start-Sleep -Seconds 5
    Set-Location ".."
}

# Preparar backend
$backendPath = Get-Location
$venvPath = Join-Path $backendPath ".venv"
$pythonExe = Join-Path $venvPath "Scripts\python.exe"
$pipExe = Join-Path $venvPath "Scripts\pip.exe"

# Verificar si el entorno virtual está completo
if (-not (Test-Path $pythonExe) -or -not (Test-Path $pipExe)) {
    Write-Host "Configurando entorno virtual..." -ForegroundColor Yellow
    
    # Eliminar .venv corrupto si existe usando cmd (más confiable)
    if (Test-Path $venvPath) {
        cmd /c "rmdir /s /q `"$venvPath`"" 2>$null
        Start-Sleep -Seconds 1
    }
    
    # Crear nuevo entorno
    python -m venv .venv
    Start-Sleep -Seconds 2
    
    # Instalar dependencias
    Write-Host "Instalando dependencias" -ForegroundColor Yellow
    & $pythonExe -m pip install --upgrade pip --quiet
    & $pipExe install -r requirements.txt --quiet
    Write-Host "Backend configurado" -ForegroundColor Green
} else {
    # Verificar si Flask está instalado
    $flaskInstalled = & $pythonExe -c "import flask" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Instalando dependencias..." -ForegroundColor Yellow
        & $pipExe install -r requirements.txt --quiet
    }
}

# Preparar frontend
$frontendPath = Join-Path $backendPath "..\Proyecto Front\proyecto-is2"
if (-not (Test-Path "$frontendPath\node_modules")) {
    Write-Host "Configurando frontend..." -ForegroundColor Yellow
    Set-Location $frontendPath
    npm install
    Set-Location $backendPath
}

Write-Host ""
Write-Host "=== Iniciando servidores ===" -ForegroundColor Green
Write-Host "Backend: http://localhost:5000" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host ""
Write-Host "Presiona Ctrl+C para detener ambos servidores" -ForegroundColor Yellow
Write-Host ""

# Crear scripts temporales
$backendScript = @"
Set-Location '$backendPath'
`$env:DATABASE_URL = 'postgresql://admin:admin123@localhost:5432/ingesoft2'
`$env:FLASK_APP = 'app.py'
`$env:FLASK_ENV = 'development'
`$env:PYTHONPATH = '$backendPath'
& '$pythonExe' app.py
"@

$frontendScript = @"
Set-Location '$frontendPath'
npm run dev
"@

# Guardar scripts
$backendScript | Out-File -FilePath "temp-backend.ps1" -Encoding UTF8
$frontendScript | Out-File -FilePath "temp-frontend.ps1" -Encoding UTF8

# Función de limpieza
$cleanup = {
    Write-Host "`n`nDeteniendo servidores..." -ForegroundColor Yellow
    Get-Job | Stop-Job
    Get-Job | Remove-Job
    Remove-Item "temp-backend.ps1" -ErrorAction SilentlyContinue
    Remove-Item "temp-frontend.ps1" -ErrorAction SilentlyContinue
}

Register-EngineEvent -SourceIdentifier PowerShell.Exiting -Action $cleanup | Out-Null

try {
    # Iniciar Backend
    $backendJob = Start-Job -ScriptBlock {
        Set-Location $using:backendPath
        & powershell.exe -NoProfile -File "temp-backend.ps1"
    }

    # Iniciar Frontend
    $frontendJob = Start-Job -ScriptBlock {
        Set-Location $using:backendPath
        & powershell.exe -NoProfile -File "temp-frontend.ps1"
    }

    Start-Sleep -Seconds 3

    # Mostrar logs en tiempo real
    while ($true) {
        $backendOutput = Receive-Job -Job $backendJob
        $frontendOutput = Receive-Job -Job $frontendJob
        
        if ($backendOutput) {
            Write-Host "[BACKEND] " -ForegroundColor Blue -NoNewline
            Write-Host $backendOutput
        }
        
        if ($frontendOutput) {
            Write-Host "[FRONTEND] " -ForegroundColor Magenta -NoNewline
            Write-Host $frontendOutput
        }
        
        if ($backendJob.State -eq 'Failed' -or $frontendJob.State -eq 'Failed') {
            Write-Host "Error: Algún servidor falló" -ForegroundColor Red
            break
        }
        
        Start-Sleep -Milliseconds 500
    }
}
finally {
    & $cleanup
}
