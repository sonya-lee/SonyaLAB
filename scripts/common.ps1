function Get-SonyaLabPortOwner {
    param([Parameter(Mandatory=$true)][int]$Port)

    $connection = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $connection) { return $null }

    $process = Get-Process -Id $connection.OwningProcess -ErrorAction SilentlyContinue
    $command = (Get-CimInstance Win32_Process -Filter "ProcessId=$($connection.OwningProcess)" -ErrorAction SilentlyContinue).CommandLine
    [pscustomobject]@{
        Port = $Port
        PID = $connection.OwningProcess
        ProcessName = if ($process) { $process.ProcessName } else { "unknown" }
        CommandLine = $command
        IsSonyaLab = [bool]($command -and $command -like "*SonyaLAB*")
    }
}

function Assert-SonyaLabPortAvailable {
    param(
        [Parameter(Mandatory=$true)][int]$Port,
        [Parameter(Mandatory=$true)][string]$Component
    )

    $owner = Get-SonyaLabPortOwner -Port $Port
    if (-not $owner) { return }

    $kind = if ($owner.IsSonyaLab) { "another Sonya Lab process" } else { "another application" }
    throw "$Component cannot start: port $Port is already used by $kind ($($owner.ProcessName), PID $($owner.PID)). No process was stopped. Run .\scripts\status.ps1 for details."
}

function Read-OwnedPid {
    param([Parameter(Mandatory=$true)][string]$PidFile)
    if (-not (Test-Path $PidFile)) { return $null }
    $raw = (Get-Content $PidFile -ErrorAction SilentlyContinue | Select-Object -First 1)
    $parsed = 0
    if (-not [int]::TryParse([string]$raw, [ref]$parsed)) {
        Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
        return $null
    }
    return $parsed
}
