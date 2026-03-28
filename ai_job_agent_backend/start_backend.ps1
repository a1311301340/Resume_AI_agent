$ErrorActionPreference = "Stop"

$backendDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvDir = Join-Path $backendDir ".venv"
$venvPython = Join-Path $venvDir "Scripts\\python.exe"
$requirements = Join-Path $backendDir "requirements.txt"
$runFile = Join-Path $backendDir "run.py"
$backendPort = 8010

function Get-PythonLauncher {
    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCmd) {
        return @("python")
    }

    $pyCmd = Get-Command py -ErrorAction SilentlyContinue
    if ($pyCmd) {
        return @("py", "-3")
    }

    throw "Python was not found. Please install Python 3.10+ and try again."
}

function Get-ListeningPidsByPort([int]$port) {
    $hits = netstat -ano -p TCP | Select-String ":$port"
    $pids = @()
    foreach ($line in $hits) {
        $text = $line.ToString()
        if ($text -match "LISTENING\s+(\d+)$") {
            $pids += [int]$Matches[1]
        }
    }
    return $pids | Sort-Object -Unique
}

if (-not (Test-Path -LiteralPath $venvPython)) {
    Write-Host "No virtual environment found. Creating .venv ..."
    $launcher = Get-PythonLauncher
    if ($launcher[0] -eq "python") {
        & python -m venv $venvDir
    } else {
        & py -3 -m venv $venvDir
    }
}

if (-not (Test-Path -LiteralPath $venvPython)) {
    throw "Virtual environment creation failed: $venvPython not found."
}

$occupiedPids = Get-ListeningPidsByPort -port $backendPort
if ($occupiedPids.Count -gt 0) {
    $pidText = ($occupiedPids -join ", ")
    throw "Port $backendPort is already in use by PID(s): $pidText. Stop them first, then rerun start_backend.ps1."
}

Write-Host "Installing backend dependencies ..."
& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r $requirements

Write-Host "Starting backend service ..."
& $venvPython $runFile
