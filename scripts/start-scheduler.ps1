$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Runtime = Join-Path $Root "runtime"
$Logs = Join-Path $Root "logs"
New-Item -ItemType Directory -Force $Runtime, $Logs | Out-Null
$PidFile = Join-Path $Runtime "scheduler.pid"
if (Test-Path $PidFile) {
    $ExistingId = [int](Get-Content $PidFile)
    if (Get-Process -Id $ExistingId -ErrorAction SilentlyContinue) { throw "Sonya Lab scheduler is already running (PID $ExistingId)." }
    Remove-Item $PidFile
}
$Python = Join-Path $Root "backend\.venv\Scripts\python.exe"
$Process = Start-Process -FilePath $Python -ArgumentList "-m","app.scheduler.runner" -WorkingDirectory (Join-Path $Root "backend") -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $Logs "scheduler.out.log") -RedirectStandardError (Join-Path $Logs "scheduler.err.log")
Start-Sleep -Seconds 2
$Process.Refresh()
if ($Process.HasExited) { throw "Scheduler failed to start. Check logs\scheduler.err.log." }
$Process.Id | Set-Content $PidFile
Write-Host "Sonya Lab scheduler started (PID $($Process.Id))."
