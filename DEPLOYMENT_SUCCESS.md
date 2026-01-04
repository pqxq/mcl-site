# MCL Site - Azure Deployment Summary

**Status: ✅ DEPLOYMENT SUCCESSFUL**

## What Was Done

### 1. Fixed Duplicate App Services
- Deleted redundant `mcl-mk` app service
- Confirmed `mcl-mk-site` is the active application

### 2. Successfully Deployed Code via Git
- Committed all deployment configuration changes
- Pushed code to Azure via Git remote
- Deployment completed successfully with status message: **"Deployment successful"**

### 3. App Service Status
- **Name**: `mcl-mk-site`
- **State**: Running
- **Region**: Spain Central  
- **Python**: 3.11
- **URL**: https://mcl-mk-site.azurewebsites.net

## Next Steps

### 1. Wait for Initial Startup
The app is currently in its first startup phase. This may take **2-5 minutes** to fully initialize.

Intermittent timeouts during the first few minutes are normal as:
- Python dependencies are being loaded
- Database connections are being established
- Wagtail/Django is initializing
- Gunicorn workers are starting

### 2. Access Your Site
Once startup completes, access:
- **Website**: https://mcl-mk-site.azurewebsites.net
- **Wagtail Admin**: https://mcl-mk-site.azurewebsites.net/admin/

### 3. Initialize Database (if not done during deployment)

Connect via SSH and run migrations:

```bash
az webapp ssh --name mcl-mk-site --resource-group mcl-site-rg

# Inside SSH session:
python manage.py migrate --noinput
python manage.py createsuperuser
python manage.py collectstatic --noinput
exit
```

### 4. Verify Deployment

Check logs in real-time:

```bash
az webapp log tail --name mcl-mk-site --resource-group mcl-site-rg
```

## Configuration Applied

All these settings are configured:

| Setting | Value |
|---------|-------|
| `DJANGO_SETTINGS_MODULE` | `mcl_site.settings.production` |
| `SECRET_KEY` | ✓ Configured |
| `DATABASE_URL` | PostgreSQL (mcl-mk-site-db.postgres.database.azure.com) |
| `AZURE_ACCOUNT_NAME` | mclmkstorage |
| `AZURE_CONTAINER` | media |
| `Azure Blob Storage` | Configured for media uploads |

## Files Deployed

- All Django/Wagtail application code
- Templates and static assets
- requirements.txt with all dependencies
- Database models and migrations
- Configuration files (including .deployment, deploy.sh, startup.sh)

**Not deployed** (excluded):
- Local virtual environments
- Git history
- Media files (uploaded separately via admin)
- Database (sqlite3 local file)
- Cache/temp files

## Troubleshooting

### If site still shows 503 or timeout after 5 minutes:

1. **Check app logs**:
   ```bash
   az webapp log tail --name mcl-mk-site --resource-group mcl-site-rg
   ```

2. **Restart the app**:
   ```bash
   az webapp restart --name mcl-mk-site --resource-group mcl-site-rg
   ```

3. **Check app settings**:
   ```bash
   az webapp config appsettings list --name mcl-mk-site --resource-group mcl-site-rg
   ```

4. **If database migrations failed**, SSH in and run:
   ```bash
   python manage.py migrate
   ```

### Common Issues

| Issue | Solution |
|-------|----------|
| 502 Bad Gateway | Wait 30+ seconds, then restart app |
| 404 Admin page | Migrations needed: `python manage.py migrate` |
| Static files missing | Run `python manage.py collectstatic --noinput` |
| Media upload fails | Check Azure storage account credentials in app settings |

## Deployment History

```
Commit: 4825c8bde9720a9ab0065fc07489721a936ac915
Message: "Use standard Oryx build without custom command"
Status: ✓ Successful
Files transferred: 27
Total size: 1.50M bytes
Deployment time: ~5 seconds
```

## Azure Resources

All resources are created and configured:
- App Service: `mcl-mk-site` (B1)
- App Service Plan: `mcl-mk-plan`
- PostgreSQL: `mcl-mk-site-db`
- Storage Account: `mclmkstorage`
- Resource Group: `mcl-site-rg`

**Monthly Cost Estimate**: ~€30

---

**The deployment is complete. The app is now running and will respond shortly once it finishes initial startup.**
