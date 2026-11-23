param (
    [Parameter(Mandatory=$false)]
    [string]$AwsIp,

    [Parameter(Mandatory=$false)]
    [switch]$Frontend,

    [Parameter(Mandatory=$false)]
    [switch]$Backend,

    [Parameter(Mandatory=$false)]
    [switch]$All
)

$ProjectRoot = $PSScriptRoot
$envFile = Join-Path $ProjectRoot ".env"

function Update-EnvVar {
    param([string]$Key, [string]$Value)
    if (Test-Path $envFile) {
        $lines = Get-Content $envFile
        $found = $false
        $newLines = @()
        foreach ($line in $lines) {
            if ($line -match "^$Key=") {
                $newLines += "$Key=$Value"
                $found = $true
            } else {
                $newLines += $line
            }
        }
        if (-not $found) {
            $newLines += "$Key=$Value"
        }
        $newLines | Set-Content -Path $envFile -Encoding UTF8
        Write-Host "[+] Persisted $Key to .env: $Value" -ForegroundColor Green
    }
}

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   DocSync AI DevOps Intelligence Platform Launcher" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Handle Dynamic AWS EC2 IP
if (-not [string]::IsNullOrWhiteSpace($AwsIp)) {
    $cleanIp = $AwsIp.Trim()
    $env:OLLAMA_BASE_URL = "http://$cleanIp:11434"
    Update-EnvVar -Key "OLLAMA_BASE_URL" -Value $env:OLLAMA_BASE_URL
    Write-Host "[+] Configured AWS IP: $cleanIp" -ForegroundColor Green
    Write-Host "[+] OLLAMA_BASE_URL: $env:OLLAMA_BASE_URL" -ForegroundColor Green
} else {
    if (Test-Path $envFile) {
        Get-Content $envFile | ForEach-Object {
            if ($_ -match "^OLLAMA_BASE_URL=(.+)$") {
                $env:OLLAMA_BASE_URL = $matches[1].Trim()
                Write-Host "[i] Current AWS EC2 OLLAMA_BASE_URL: $env:OLLAMA_BASE_URL" -ForegroundColor Gray
            }
        }
    }
}

# Prompt menu if no flags passed
if (-not $Frontend -and -not $Backend -and -not $All) {
    Write-Host ""
    Write-Host "Select option to run:" -ForegroundColor Yellow
    Write-Host " [1] Frontend (Streamlit Web UI on port 8501) [Default]" -ForegroundColor White
    Write-Host " [2] Backend (Docker Container via docker-compose)" -ForegroundColor White
    Write-Host " [3] Both (Docker Backend + Frontend)" -ForegroundColor White
    Write-Host " [4] Set / Change AWS EC2 IP (Current: $env:OLLAMA_BASE_URL)" -ForegroundColor White
    
    $choice = Read-Host "Enter option (1, 2, 3, or 4)"
    if ([string]::IsNullOrWhiteSpace($choice) -or $choice -eq "1") {
        $Frontend = $true
    } elseif ($choice -eq "2") {
        $Backend = $true
    } elseif ($choice -eq "3") {
        $All = $true
    } elseif ($choice -eq "4") {
        $newIp = Read-Host "Enter new AWS EC2 Public IPv4"
        if (-not [string]::IsNullOrWhiteSpace($newIp)) {
            $cleanIp = $newIp.Trim()
            $env:OLLAMA_BASE_URL = "http://$cleanIp:11434"
            Update-EnvVar -Key "OLLAMA_BASE_URL" -Value $env:OLLAMA_BASE_URL
            Write-Host "[+] AWS IP set and saved to .env: $cleanIp" -ForegroundColor Green
        }
        $Frontend = $true
    }
}

# 2. Launch Backend (Docker)
if ($Backend -or $All) {
    Write-Host ""
    Write-Host ">> Starting Docker Backend Container..." -ForegroundColor Cyan
    try {
        $dockerCheck = docker ps 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[!] Docker Desktop engine is not running." -ForegroundColor Yellow
            Write-Host "    Starting Docker Desktop..." -ForegroundColor Yellow
            Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe" -ErrorAction SilentlyContinue
            Write-Host "    Waiting 15 seconds for Docker engine to initialize..." -ForegroundColor Yellow
            Start-Sleep -Seconds 15
        }
        
        Write-Host "[+] Executing: docker compose up -d" -ForegroundColor Green
        docker compose up -d
        Write-Host "[OK] Docker backend container active!" -ForegroundColor Green
    } catch {
        Write-Host "[!] Docker error: $_" -ForegroundColor Red
        Write-Host "    Make sure Docker Desktop is started." -ForegroundColor Yellow
    }
}

# 3. Launch Frontend (Streamlit)
if ($Frontend -or $All) {
    Write-Host ""
    Write-Host ">> Starting Streamlit Frontend..." -ForegroundColor Cyan
    $PythonExe = Join-Path $ProjectRoot "venv\Scripts\python.exe"
    $AppScript = Join-Path $ProjectRoot "dashboard\streamlit_app.py"

    if (-not (Test-Path $PythonExe)) {
        Write-Host "[!] Using system python." -ForegroundColor Yellow
        $PythonExe = "python"
    }

    Write-Host "[+] Serving dashboard at http://localhost:8501" -ForegroundColor Green
    & $PythonExe -m streamlit run $AppScript --server.port 8501
}
