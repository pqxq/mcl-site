# MCL Site - Azure Deployment Complete

## ✅ Resources Created Successfully

All Azure resources are created and running in **Spain Central**:

- **Resource Group**: `mcl-site-rg`
- **App Service**: `mcl-mk-site` (B1 tier, Linux)
  - URL: https://mcl-mk-site.azurewebsites.net
- **PostgreSQL Database**: `mcl-mk-site-db`
  - Connection: `postgres://mcladmin:MclAdmin2026!@mcl-mk-site-db.postgres.database.azure.com:5432/mcl_db`
- **Storage Account**: `mclmkstorage`
  - Container: `media` (for uploaded images/files)

## ⚙️ Configuration Applied

All environment variables are set:
- `DJANGO_SETTINGS_MODULE=mcl_site.settings.production`
- `SECRET_KEY` (configured)
- `DATABASE_URL` (PostgreSQL connection)
- `AZURE_ACCOUNT_NAME`, `AZURE_ACCOUNT_KEY`, `AZURE_CONTAINER` (for media storage)
- `DISABLE_COLLECTSTATIC=1` (to avoid build errors)

## 🚀 Final Deployment Step

The code needs to be deployed. Use **VS Code Azure Extension** for easiest deployment:

### Option 1: Using VS Code Azure Extension (Recommended)

1. Install "Azure App Service" extension in VS Code
2. Sign in to Azure (Ctrl+Shift+P → "Azure: Sign In")
3. Right-click on `d:\mcl-site` folder
4. Select "Deploy to Web App..."
5. Choose subscription and select `mcl-mk-site`
6. Confirm deployment

### Option 2: Using Azure Portal

1. Go to https://portal.azure.com
2. Navigate to App Service → `mcl-mk-site`
3. Go to "Deployment Center" in left menu
4. Choose "Local Git/FTPS credentials"
5. Get credentials and use FTP client to upload files

### Option 3: Using PowerShell with Kudu

```powershell
cd D:\mcl-site

# Get publish profile
az webapp deployment list-publishing-profiles `
  --name mcl-mk-site `
  --resource-group mcl-site-rg `
  --xml > publish-profile.xml

# Use the profile with your FTP client or deployment tool
```

## 📋 Post-Deployment Steps

Once deployed, run these commands:

```powershell
# SSH into the app
az webapp ssh --name mcl-mk-site --resource-group mcl-site-rg

# Inside SSH session:
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

## 🎯 Access Your Site

- **Website**: https://mcl-mk-site.azurewebsites.net
- **Admin Panel**: https://mcl-mk-site.azurewebsites.net/admin/

## 💰 Monthly Cost Estimate

- App Service B1: ~€13/month
- PostgreSQL B1ms: ~€15/month
- Storage (LRS): ~€2/month
- **Total**: ~€30/month

## 🔧 Useful Commands

```powershell
# View logs
az webapp log tail --name mcl-mk-site --resource-group mcl-site-rg

# Restart app
az webapp restart --name mcl-mk-site --resource-group mcl-site-rg

# Stop app
az webapp stop --name mcl-mk-site --resource-group mcl-site-rg

# Start app
az webapp start --name mcl-mk-site --resource-group mcl-site-rg

# Scale up to P1V2 (better performance)
az appservice plan update --name mcl-mk-plan --resource-group mcl-site-rg --sku P1V2
```

---

**Note**: The deployment package is ready at `D:\deploy-final.zip`. Use VS Code Azure extension for the easiest deployment experience.
