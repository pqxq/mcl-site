# Azure Deployment Guide for MCL Site

## Prerequisites

1. **Azure Account** with an active subscription
2. **Azure CLI** installed (`az --version`)
3. **Python 3.11+** for local development

## Quick Deploy Options

### Option 1: Deploy with Azure CLI (Recommended)

```bash
# Login to Azure
az login

# Create resource group
az group create --name mcl-site-rg --location westeurope

# Deploy infrastructure using Bicep
az deployment group create \
  --resource-group mcl-site-rg \
  --template-file azure/main.bicep \
  --parameters webAppName=mcl-mk \
  --parameters postgresAdminPassword=<your-secure-password> \
  --parameters djangoSecretKey=<your-secret-key>

# Deploy the application
az webapp up --name mcl-mk --resource-group mcl-site-rg --runtime "PYTHON:3.11"
```

### Option 2: Deploy with Docker

```bash
# Build and push to Azure Container Registry
az acr build --registry <your-acr-name> --image mcl-site:latest .

# Configure App Service to use the container
az webapp config container set \
  --name mcl-mk \
  --resource-group mcl-site-rg \
  --docker-custom-image-name <your-acr-name>.azurecr.io/mcl-site:latest
```

### Option 3: GitHub Actions CI/CD

1. Go to Azure Portal > App Service > Deployment Center
2. Download the Publish Profile
3. Add it as `AZURE_WEBAPP_PUBLISH_PROFILE` secret in GitHub
4. Push to `main` branch to trigger deployment

## Required Environment Variables

Configure these in Azure Portal > App Service > Configuration > Application settings:

| Variable | Description | Example |
|----------|-------------|---------|
| `DJANGO_SETTINGS_MODULE` | Settings module | `mcl_site.settings.production` |
| `SECRET_KEY` | Django secret key | Generate with Python |
| `DATABASE_URL` | PostgreSQL connection string | `postgres://user:pass@host:5432/db?sslmode=require` |
| `AZURE_ACCOUNT_NAME` | Storage account name | `mclstorage` |
| `AZURE_ACCOUNT_KEY` | Storage account key | From Azure Portal |
| `AZURE_CONTAINER` | Blob container name | `media` |

## Generate Secret Key

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Database Setup

After deployment, run migrations:

```bash
# SSH into App Service
az webapp ssh --name mcl-mk --resource-group mcl-site-rg

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

## Post-Deployment Checklist

- [ ] Verify site is accessible at `https://mcl-mk.azurewebsites.net`
- [ ] Login to Wagtail admin at `/admin/`
- [ ] Test media upload (should go to Azure Blob Storage)
- [ ] Configure custom domain (optional)
- [ ] Enable Azure Application Insights for monitoring
- [ ] Set up backup for PostgreSQL database
- [ ] Configure SSL certificate for custom domain

## Scaling

```bash
# Scale up (more resources)
az appservice plan update --name mcl-mk-plan --resource-group mcl-site-rg --sku P1V2

# Scale out (more instances)
az webapp scale --name mcl-mk --resource-group mcl-site-rg --instance-count 2
```

## Troubleshooting

### View Logs
```bash
az webapp log tail --name mcl-mk --resource-group mcl-site-rg
```

### Enable Debug Logging
```bash
az webapp config appsettings set --name mcl-mk --resource-group mcl-site-rg --settings DJANGO_LOG_LEVEL=DEBUG
```

### Check Application Health
```bash
curl -I https://mcl-mk.azurewebsites.net
```

## Cost Optimization

- Use **B1** tier for staging/development (~$13/month)
- Use **P1V2** tier for production (~$73/month)
- Consider **Reserved Instances** for 1-3 year savings (up to 65%)
- Use **Azure CDN** for static files to reduce App Service load
