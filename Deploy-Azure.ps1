#!/usr/bin/env pwsh
# MCL Site Azure Deployment Script
# This script deploys the MCL Site to Azure App Service

param(
    [string]$AppName = "mcl-mk-site",
    [string]$ResourceGroup = "mcl-site-rg"
)

$ErrorActionPreference = "Stop"

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "MCL Site - Azure Deployment" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Verify authentication
Write-Host "Step 1: Verifying Azure authentication..." -ForegroundColor Yellow
try {
    $account = az account show 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Not authenticated. Run: az login" -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ Authenticated as: $(($account | ConvertFrom-Json).user.name)" -ForegroundColor Green
} catch {
    Write-Host "✗ Authentication error: $_" -ForegroundColor Red
    exit 1
}

# Step 2: Verify resources exist
Write-Host "`nStep 2: Verifying Azure resources..." -ForegroundColor Yellow
$app = az webapp show --name $AppName --resource-group $ResourceGroup 2>&1 | ConvertFrom-Json
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ App Service: $($app.name) (Status: $($app.state))" -ForegroundColor Green
    Write-Host "  URL: https://$($app.defaultHostName)" -ForegroundColor Cyan
} else {
    Write-Host "✗ App Service not found" -ForegroundColor Red
    exit 1
}

# Step 3: Create deployment package
Write-Host "`nStep 3: Creating deployment package..." -ForegroundColor Yellow
$zipPath = "D:\mcl-deploy.zip"
if (Test-Path $zipPath) {
    Remove-Item $zipPath -Force
}

$excludePatterns = @('venv', 'site_venv', '.git', 'media', '__pycache__', '.pytest_cache', 'db.sqlite3', '.env', '*.egg-info', 'node_modules', '.vscode', '.idea')

Get-ChildItem -Path "D:\mcl-site" -Recurse -File | Where-Object {
    $file = $_
    $excluded = $false
    foreach ($pattern in $excludePatterns) {
        if ($file.FullName -match [regex]::Escape($pattern)) {
            $excluded = $true
            break
        }
    }
    -not $excluded
} | Compress-Archive -DestinationPath $zipPath -Force

$size = [math]::Round((Get-Item $zipPath).Length / 1MB, 2)
Write-Host "✓ Package created: $zipPath ($size MB)" -ForegroundColor Green

# Step 4: Deploy to Azure
Write-Host "`nStep 4: Deploying to Azure..." -ForegroundColor Yellow
Write-Host "This may take a few minutes..." -ForegroundColor Gray

$deployResult = az webapp deploy `
    --resource-group $ResourceGroup `
    --name $AppName `
    --src-path $zipPath `
    --type zip `
    --async 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Deployment initiated successfully" -ForegroundColor Green
    Write-Host "  The app will be available at: https://$($app.defaultHostName)" -ForegroundColor Cyan
} else {
    Write-Host "✗ Deployment failed:" -ForegroundColor Red
    Write-Host $deployResult -ForegroundColor Red
    exit 1
}

# Step 5: Wait and verify
Write-Host "`nStep 5: Waiting for app to start (this may take 2-5 minutes)..." -ForegroundColor Yellow
$maxWait = 300  # 5 minutes
$elapsed = 0
$interval = 10

while ($elapsed -lt $maxWait) {
    Start-Sleep -Seconds $interval
    $elapsed += $interval
    
    try {
        $response = Invoke-WebRequest -Uri "https://$($app.defaultHostName)" -SkipHttpErrorCheck -TimeoutSec 5
        if ($response.StatusCode -in @(200, 404, 500)) {
            Write-Host "✓ Application is responding!" -ForegroundColor Green
            Write-Host ""
            Write-Host "==================================" -ForegroundColor Green
            Write-Host "✓ Deployment Complete!" -ForegroundColor Green
            Write-Host "==================================" -ForegroundColor Green
            Write-Host ""
            Write-Host "Next Steps:" -ForegroundColor Cyan
            Write-Host "1. Run database migrations:" -ForegroundColor White
            Write-Host "   az webapp ssh --name $AppName --resource-group $ResourceGroup" -ForegroundColor Gray
            Write-Host "   python manage.py migrate" -ForegroundColor Gray
            Write-Host ""
            Write-Host "2. Create superuser:" -ForegroundColor White
            Write-Host "   python manage.py createsuperuser" -ForegroundColor Gray
            Write-Host ""
            Write-Host "3. Collect static files:" -ForegroundColor White
            Write-Host "   python manage.py collectstatic --noinput" -ForegroundColor Gray
            Write-Host ""
            Write-Host "4. View logs:" -ForegroundColor White
            Write-Host "   az webapp log tail --name $AppName --resource-group $ResourceGroup" -ForegroundColor Gray
            Write-Host ""
            Write-Host "Website: https://$($app.defaultHostName)" -ForegroundColor Cyan
            Write-Host "Admin: https://$($app.defaultHostName)/admin/" -ForegroundColor Cyan
            exit 0
        }
    } catch {
        # App not ready yet
    }
    
    Write-Host "  Waiting... ($elapsed/$maxWait seconds)" -ForegroundColor Gray
}

Write-Host "⚠ Timeout waiting for app to respond" -ForegroundColor Yellow
Write-Host "The deployment may still be in progress. Check the portal or run:" -ForegroundColor White
Write-Host "az webapp log tail --name $AppName --resource-group $ResourceGroup" -ForegroundColor Gray
