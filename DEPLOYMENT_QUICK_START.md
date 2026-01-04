# MCL Site Azure Deployment Guide - Quick Start

Your Azure infrastructure is **fully configured and ready**. All resources (App Service, PostgreSQL, Storage) are running in Spain Central.

## Quick Deployment (Easiest Option)

### Option 1: Using PowerShell Script (Recommended)

```powershell
cd D:\mcl-site
.\Deploy-Azure.ps1
```

This script will:
- Verify your Azure authentication
- Create a deployment package
- Deploy to Azure App Service
- Wait for the app to start
- Show you next steps

### Option 2: Manual Deployment

If the script doesn't work, use this command:

```powershell
cd D:\mcl-site
az webapp deploy --resource-group mcl-site-rg --name mcl-mk-site --src-path "D:\mcl-deploy.zip" --type zip
```

## Post-Deployment Setup

After deployment completes, you need to initialize the database and create an admin user.

### Step 1: Connect to the App via SSH

```powershell
az webapp ssh --name mcl-mk-site --resource-group mcl-site-rg
```

You'll now be in a bash shell inside the app container.

### Step 2: Run Database Migrations

```bash
python manage.py migrate --noinput
```

### Step 3: Create Superuser (Admin Account)

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### Step 4: Collect Static Files (Optional)

```bash
python manage.py collectstatic --noinput
```

### Step 5: Exit SSH

```bash
exit
```

## Verify Deployment

Once complete, test these URLs:

- **Website**: https://mcl-mk-site.azurewebsites.net
- **Wagtail Admin**: https://mcl-mk-site.azurewebsites.net/admin/

Login with the superuser credentials you created.

## Monitoring & Troubleshooting

### View Real-Time Logs

```powershell
az webapp log tail --name mcl-mk-site --resource-group mcl-site-rg
```

### Restart the App

```powershell
az webapp restart --name mcl-mk-site --resource-group mcl-site-rg
```

### Check Current Settings

```powershell
az webapp config appsettings list --name mcl-mk-site --resource-group mcl-site-rg
```

## Configuration Details

### Current Settings

| Setting | Value |
|---------|-------|
| **App Service** | mcl-mk-site (B1, Linux) |
| **Location** | Spain Central |
| **Python** | 3.11 |
| **Database** | PostgreSQL (Flexible Server) |
| **Storage** | Azure Blob Storage (media container) |

### Environment Variables

All required environment variables are already configured:

- `DJANGO_SETTINGS_MODULE=mcl_site.settings.production`
- `SECRET_KEY` (configured)
- `DATABASE_URL` (PostgreSQL connection)
- `AZURE_ACCOUNT_NAME`, `AZURE_ACCOUNT_KEY` (Blob storage)

## Common Issues

### 503 Service Unavailable

The app is starting up. Wait 1-2 minutes and refresh.

### Database Connection Error

Run migrations:

```bash
az webapp ssh --name mcl-mk-site --resource-group mcl-site-rg
python manage.py migrate
exit
```

### Media Files Not Uploading

Check that storage account credentials are set:

```powershell
az webapp config appsettings show --name mcl-mk-site --resource-group mcl-site-rg `
  | Select-String "AZURE_ACCOUNT"
```

### Static Files 404

Collect static files:

```bash
az webapp ssh --name mcl-mk-site --resource-group mcl-site-rg
python manage.py collectstatic --noinput
exit
```

## Advanced Configuration

### Scaling Up

If you need better performance:

```powershell
# Upgrade from B1 to P1V2
az appservice plan update --name mcl-mk-plan --resource-group mcl-site-rg --sku P1V2
```

### Custom Domain

To add your custom domain:

```powershell
az webapp config hostname add --webapp-name mcl-mk-site --resource-group mcl-site-rg `
  --hostname your-domain.com
```

Then update DNS records at your domain provider to point to Azure.

### Enable HTTPS with Custom Certificate

Azure automatically provides an Azure-managed certificate for `.azurewebsites.net` URLs.

For custom domains, use Azure's free managed certificate:

```powershell
az webapp config ssl bind --name mcl-mk-site --resource-group mcl-site-rg `
  --certificate-thumbprint <thumbprint> --ssl-type SNI
```

## Cost Estimation

Monthly cost (approx):

| Resource | SKU | Cost |
|----------|-----|------|
| App Service | B1 | €13 |
| PostgreSQL | B1ms | €15 |
| Storage | LRS | €2 |
| **Total** | | **~€30/month** |

## Support & Documentation

- [Azure App Service Documentation](https://docs.microsoft.com/azure/app-service/)
- [Django Deployment Guide](https://docs.djangoproject.com/en/5.1/howto/deployment/)
- [Wagtail Deployment](https://docs.wagtail.org/en/stable/advanced_topics/deploying/)

---

**Need help?** Check the app logs first:

```powershell
az webapp log tail --name mcl-mk-site --resource-group mcl-site-rg
```
