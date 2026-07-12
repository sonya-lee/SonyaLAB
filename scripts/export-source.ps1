$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Parent = Split-Path -Parent $Root
$Output = Join-Path $Parent "SonyaLAB-source.zip"
$Temp = Join-Path $env:TEMP ("SonyaLAB-export-" + [guid]::NewGuid().ToString("N"))
$Dest = Join-Path $Temp "SonyaLAB"
New-Item -ItemType Directory -Force $Dest | Out-Null

$ExcludeDirs = @(".git", ".venv", "node_modules", "runtime", "logs", "data", "dist", "__pycache__", ".pytest_cache")
$ExcludeFiles = @(".env", "*.db", "*.sqlite", "*.sqlite3", "*.pyc")

$robocopyArgs = @($Root, $Dest, "/E", "/NFL", "/NDL", "/NJH", "/NJS", "/NP")
foreach ($dir in $ExcludeDirs) { $robocopyArgs += @("/XD", $dir) }
$robocopyArgs += "/XF"
$robocopyArgs += $ExcludeFiles
& robocopy @robocopyArgs | Out-Null
if ($LASTEXITCODE -ge 8) { throw "Source export failed with robocopy code $LASTEXITCODE" }

if (Test-Path $Output) { Remove-Item $Output -Force }
Compress-Archive -Path $Dest -DestinationPath $Output -CompressionLevel Optimal
Remove-Item $Temp -Recurse -Force
Write-Host "Created sanitized source archive: $Output"
