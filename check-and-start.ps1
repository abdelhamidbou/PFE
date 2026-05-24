# DermaFlow AI Backend Auto-Start Script
# This script checks if backend is running, and starts it if not

$API_URL = "http://localhost:8000/health"
$BACKEND_DIR = "C:\Users\Pc\Desktop\clinicflow-ai\backend"

function Test-BackendRunning {
    try {
        $response = Invoke-WebRequest -Uri $API_URL -UseBasicParsing -TimeoutSec 2
        return $response.StatusCode -eq 200
    } catch {
        return $false
    }
}

function Start-Backend {
    Write-Host "Starting DermaFlow AI Backend..." -ForegroundColor Green

    # Start in new minimized window
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = "powershell.exe"
    $psi.Arguments = "-WindowStyle Minimized -Command `"cd '$BACKEND_DIR'; .\venv\Scripts\Activate; uvicorn main:app --reload --host 0.0.0.0 --port 8000`""
    $psi.WorkingDirectory = $BACKEND_DIR

    [System.Diagnostics.Process]::Start($psi) | Out-Null

    # Wait for startup
    Write-Host "Waiting for server to start..." -ForegroundColor Yellow
    Start-Sleep -Seconds 3

    # Check if started
    if (Test-BackendRunning) {
        Write-Host "✅ Backend is now running at http://localhost:8000" -ForegroundColor Green
        return $true
    } else {
        Write-Host "❌ Failed to start backend" -ForegroundColor Red
        return $false
    }
}

# Main logic
if (Test-BackendRunning) {
    Write-Host "✅ Backend is already running at http://localhost:8000" -ForegroundColor Green
} else {
    Write-Host "⚠️ Backend is not running" -ForegroundColor Yellow
    Start-Backend
}

Write-Host ""
Write-Host "You can now open your frontend HTML files in the browser." -ForegroundColor Cyan
