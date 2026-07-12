$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Runtime = Join-Path $Root "runtime"
foreach ($Name in @("frontend", "backend", "scheduler")) {
    $PidFile = Join-Path $Runtime "$Name.pid"
    if (-not (Test-Path $PidFile)) { continue }
    $OwnedPid = [int](Get-Content $PidFile)
    $Process = Get-Process -Id $OwnedPid -ErrorAction SilentlyContinue
    if ($Process) {
        $Command = (Get-CimInstance Win32_Process -Filter "ProcessId=$OwnedPid" -ErrorAction SilentlyContinue).CommandLine
        if (-not $Command -or $Command -notlike "*SonyaLAB*") {
            Write-Warning "Refusing to stop PID $OwnedPid because its command line cannot be verified as Sonya Lab. Remove the stale PID file manually only after checking the process."
            continue
        }
        Stop-Process -Id $OwnedPid
        Write-Host "Stopped Sonya Lab $Name (PID $OwnedPid)."
    }
    Remove-Item $PidFile -Force
}
