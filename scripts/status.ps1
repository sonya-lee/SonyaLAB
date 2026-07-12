$Root = Split-Path -Parent $PSScriptRoot
. (Join-Path $PSScriptRoot "common.ps1")
$Runtime = Join-Path $Root "runtime"
$components = foreach ($Name in @("frontend", "backend", "scheduler")) {
    $PidFile = Join-Path $Runtime "$Name.pid"
    $OwnedPid = Read-OwnedPid -PidFile $PidFile
    $process = if ($OwnedPid) { Get-Process -Id $OwnedPid -ErrorAction SilentlyContinue } else { $null }
    [pscustomobject]@{
        Component = $Name
        PID = $OwnedPid
        Running = [bool]$process
        Process = if ($process) { $process.ProcessName } else { "" }
    }
}
$components | Format-Table -AutoSize
Write-Host "Port ownership"
foreach ($Port in @(5175, 8002, 55432)) {
    $owner = Get-SonyaLabPortOwner -Port $Port
    if ($owner) { $owner | Select-Object Port,PID,ProcessName,IsSonyaLab | Format-Table -AutoSize }
    else { Write-Host "Port $Port: available" }
}
