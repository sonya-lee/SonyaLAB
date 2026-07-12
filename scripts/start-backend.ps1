$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
. (Join-Path $PSScriptRoot "common.ps1")
$Runtime = Join-Path $Root "runtime"
$Logs = Join-Path $Root "logs"
New-Item -ItemType Directory -Force $Runtime, $Logs | Out-Null
$PidFile = Join-Path $Runtime "backend.pid"
$ExistingId = Read-OwnedPid -PidFile $PidFile
if ($ExistingId) {
    if (Get-Process -Id $ExistingId -ErrorAction SilentlyContinue) { throw "Sonya Lab backend is already running (PID $ExistingId)." }
    Remove-Item $PidFile -Force
}
Assert-SonyaLabPortAvailable -Port 8002 -Component "Backend"
$Python = Join-Path $Root "backend\.venv\Scripts\python.exe"
if (-not (Test-Path $Python)) { throw "Backend virtual environment is missing. Run setup first." }
$BackendDir = Join-Path $Root "backend"
Push-Location $BackendDir
try {
    & $Python -m alembic upgrade head
    if ($LASTEXITCODE -ne 0) { throw "Database migration failed. Check backend/.env and database availability." }
} finally {
    Pop-Location
}
$Process = Start-Process -FilePath $Python -ArgumentList "-m","uvicorn","app.main:app","--host","0.0.0.0","--port","8002" -WorkingDirectory $BackendDir -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $Logs "backend.out.log") -RedirectStandardError (Join-Path $Logs "backend.err.log")
Start-Sleep -Seconds 2
$Process.Refresh()
if ($Process.HasExited) { throw "Backend failed to start. Check logs\backend.err.log. No existing port process was stopped." }
$Process.Id | Set-Content $PidFile
Write-Host "Sonya Lab backend started on http://localhost:8002 (PID $($Process.Id))."
