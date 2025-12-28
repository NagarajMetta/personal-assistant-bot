Write-Host "Checking Ngrok installation..." -ForegroundColor Cyan
$ngrokPath = "$env:LOCALAPPDATA\ngrok\ngrok.exe"
$ngrokDir = "$env:LOCALAPPDATA\ngrok"

if (Test-Path $ngrokPath) {
    Write-Host "Ngrok found: $ngrokPath" -ForegroundColor Green
} else {
    Write-Host "Installing Ngrok..." -ForegroundColor Yellow
    
    if (!(Test-Path $ngrokDir)) {
        New-Item -ItemType Directory -Path $ngrokDir | Out-Null
    }
    
    $downloadUrl = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip"
    $zipPath = "$ngrokDir\ngrok.zip"
    
    try {
        Write-Host "Downloading..." -ForegroundColor Yellow
        Invoke-WebRequest -Uri $downloadUrl -OutFile $zipPath -UseBasicParsing
        Write-Host "Extracting..." -ForegroundColor Yellow
        Expand-Archive -Path $zipPath -DestinationPath $ngrokDir -Force
        Remove-Item $zipPath
        Write-Host "Ngrok installed!" -ForegroundColor Green
    } catch {
        Write-Host "Failed to download Ngrok" -ForegroundColor Red
        Write-Host "Visit: https://ngrok.com/download" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host "`nNgrok Ready! Start bot and Ngrok in separate terminals:" -ForegroundColor Green
Write-Host "Terminal 1: python main.py" -ForegroundColor Cyan
Write-Host "Terminal 2: .\start_ngrok.ps1" -ForegroundColor Cyan
