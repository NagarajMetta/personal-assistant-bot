Write-Host "Starting Ngrok (exposing port 8000)..." -ForegroundColor Cyan
$ngrokPath = "$env:LOCALAPPDATA\ngrok\ngrok.exe"

if (!(Test-Path $ngrokPath)) {
    Write-Host "Ngrok not found. Run: .\setup_ngrok.ps1" -ForegroundColor Red
    exit 1
}

Write-Host "Press CTRL+C to stop`n" -ForegroundColor Gray
& $ngrokPath http 8000

