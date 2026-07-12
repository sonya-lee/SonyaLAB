$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Runtime = Join-Path $Root "runtime"
$Logs = Join-Path $Root "logs"
New-Item -ItemType Directory -Force $Runtime, $Logs | Out-Null
$PidFile = Join-Path $Runtime "frontend.pid"
if (Test-Path $PidFile) {
    $ExistingId = [int](Get-Content $PidFile)
    if (Get-Process -Id $ExistingId -ErrorAction SilentlyContinue) { throw "Sonya Lab frontend is already running (PID $ExistingId)." }
    Remove-Item $PidFile
}
$Node = (Get-Command node.exe -ErrorAction Stop).Source
$Vite = Join-Path $Root "frontend\node_modules\vite\bin\vite.js"
if (-not (Test-Path $Vite)) { throw "Frontend dependencies are missing. Run npm.cmd install first." }
$Process = Start-Process -FilePath $Node -ArgumentList $Vite -WorkingDirectory (Join-Path $Root "frontend") -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $Logs "frontend.out.log") -RedirectStandardError (Join-Path $Logs "frontend.err.log")
Start-Sleep -Seconds 2
$Process.Refresh()
if ($Process.HasExited) { throw "Frontend failed to start. Check logs\frontend.err.log. No existing port process was stopped." }
$Process.Id | Set-Content $PidFile
Write-Host "Sonya Lab frontend started on http://localhost:5175 (PID $($Process.Id))."
