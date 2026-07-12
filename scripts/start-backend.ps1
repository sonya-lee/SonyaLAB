$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Runtime = Join-Path $Root "runtime"
$Logs = Join-Path $Root "logs"
New-Item -ItemType Directory -Force $Runtime, $Logs | Out-Null
$PidFile = Join-Path $Runtime "backend.pid"
if (Test-Path $PidFile) {
    $ExistingId = [int](Get-Content $PidFile)
    if (Get-Process -Id $ExistingId -ErrorAction SilentlyContinue) { throw "Sonya Lab backend is already running (PID $ExistingId)." }
    Remove-Item $PidFile
}
$Python = Join-Path $Root "backend\.venv\Scripts\python.exe"
if (-not (Test-Path $Python)) { throw "Backend virtual environment is missing. Run setup first." }
$Process = Start-Process -FilePath $Python -ArgumentList "-m","uvicorn","app.main:app","--host","127.0.0.1","--port","8002" -WorkingDirectory (Join-Path $Root "backend") -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $Logs "backend.out.log") -RedirectStandardError (Join-Path $Logs "backend.err.log")
Start-Sleep -Seconds 2
$Process.Refresh()
if ($Process.HasExited) { throw "Backend failed to start. Check logs\backend.err.log. No existing port process was stopped." }
$Process.Id | Set-Content $PidFile
Write-Host "Sonya Lab backend started on http://localhost:8002 (PID $($Process.Id))."
