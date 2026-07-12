$Root = Split-Path -Parent $PSScriptRoot
foreach ($Script in @("start-backend.ps1", "start-frontend.ps1", "start-scheduler.ps1")) {
    try { & (Join-Path $PSScriptRoot $Script) }
    catch { Write-Warning $_.Exception.Message }
}
Write-Host "Sonya Lab components started independently. No other Sonya process was inspected or stopped."
