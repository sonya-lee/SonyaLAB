$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
. (Join-Path $PSScriptRoot "common.ps1")

$checks = @()
function Add-Check($Name, $Ok, $Detail) {
    $script:checks += [pscustomobject]@{ Check=$Name; OK=[bool]$Ok; Detail=$Detail }
}

$Python = Join-Path $Root "backend\.venv\Scripts\python.exe"
Add-Check "Backend virtualenv" (Test-Path $Python) $Python

$Node = Get-Command node.exe -ErrorAction SilentlyContinue
Add-Check "Node.js" ([bool]$Node) $(if ($Node) { $Node.Source } else { "node.exe not found" })

$Vite = Join-Path $Root "frontend\node_modules\vite\bin\vite.js"
Add-Check "Frontend dependencies" (Test-Path $Vite) $Vite

$BackendEnv = Join-Path $Root "backend\.env"
Add-Check "Backend .env" (Test-Path $BackendEnv) $(if (Test-Path $BackendEnv) { "configured" } else { "copy backend/.env.example to backend/.env" })

foreach ($item in @(@{Name="Frontend port"; Port=5175}, @{Name="Backend port"; Port=8002})) {
    $owner = Get-SonyaLabPortOwner -Port $item.Port
    if ($owner) {
        Add-Check $item.Name $false "port $($item.Port): $($owner.ProcessName) PID $($owner.PID), SonyaLab=$($owner.IsSonyaLab)"
    } else {
        Add-Check $item.Name $true "port $($item.Port) available"
    }
}

$dbOwner = Get-SonyaLabPortOwner -Port 55432
Add-Check "PostgreSQL host port" $true $(if ($dbOwner) { "port 55432 listening: $($dbOwner.ProcessName) PID $($dbOwner.PID)" } else { "port 55432 not listening; SQLite mode is still available" })

$checks | Format-Table -AutoSize
if ($checks | Where-Object { -not $_.OK }) {
    Write-Warning "Preflight found items that need attention. Existing processes were not stopped."
    exit 1
}
Write-Host "Sonya Lab preflight passed."
