$Root = Split-Path -Parent $PSScriptRoot
$Runtime = Join-Path $Root "runtime"
foreach ($Name in @("frontend", "backend", "scheduler")) {
    $PidFile = Join-Path $Runtime "$Name.pid"
    if (Test-Path $PidFile) {
        $OwnedPid = [int](Get-Content $PidFile)
        $Running = [bool](Get-Process -Id $OwnedPid -ErrorAction SilentlyContinue)
        [pscustomobject]@{ Component=$Name; PID=$OwnedPid; Running=$Running }
    } else {
        [pscustomobject]@{ Component=$Name; PID=$null; Running=$false }
    }
}
