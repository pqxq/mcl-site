# Deploy MCL Site to Azure - Working Solution

## ✅ All Azure Resources Are Ready

Your site infrastructure is fully configured in Azure (Spain Central).

## 🚀 Deploy Using FTP (Most Reliable Method)

### Step 1: Get FTP Credentials

Run this command to see your FTP credentials:

```powershell
$publishXml = az webapp deployment list-publishing-profiles --name mcl-mk-site --resource-group mcl-site-rg --xml
[xml]$xml = $publishXml
$ftpProfile = $xml.publishData.publishProfile | Where-Object { $_.publishMethod -eq 'FTP' }

Write-Host "=== FTP CONNECTION INFO ==="
Write-Host "Host: $($ftpProfile.publishUrl)"
Write-Host "Username: $($ftpProfile.userName)"  
Write-Host "Password: $($ftpProfile.userPWD)"
Write-Host "==========================="
```

### Step 2: Download FileZilla (Free FTP Client)

Download from: https://filezilla-project.org/download.php?type=client

### Step 3: Connect and Upload

1. Open FileZilla
2. File → Site Manager → New Site
3. Enter the FTP details from Step 1:
   - Protocol: **FTP - File Transfer Protocol**
   - Host: (from publishUrl, remove `ftps://` prefix)
   - Port: **21**
   - Encryption: **Require explicit FTP over TLS**
   - Logon Type: **Normal**
   - User: (from userName)
   - Password: (from userPWD)

4. Connect

5. Navigate remote site to: `/site/wwwroot`

6. Upload ALL files from `D:\mcl-site` **EXCEPT**:
   - `.git` folder
   - `venv` folder  
   - `media` folder
   - `db.sqlite3`
   - `__pycache__` folders
   - `.env` file
   - `*.pyc` files
   - `azure-logs*` folders
   - `*.zip` files

### Step 4: Run Post-Deployment Commands

After upload completes:

```powershell
# SSH into your app
az webapp ssh --name mcl-mk-site --resource-group mcl-site-rg

# Inside SSH, run:
cd /home/site/wwwroot
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser

# Exit SSH
exit
```

### Step 5: Restart the App

```powershell
az webapp restart --name mcl-mk-site --resource-group mcl-site-rg
```

### Step 6: Access Your Site

🌐 **Your Site**: https://mcl-mk-site.azurewebsites.net
👤 **Admin Panel**: https://mcl-mk-site.azurewebsites.net/admin/

---

## 🔄 Alternative: Use PowerShell FTP Upload Script

If you prefer automation, save this as `deploy-ftp.ps1`:

```powershell
# Get FTP credentials
$publishXml = az webapp deployment list-publishing-profiles --name mcl-mk-site --resource-group mcl-site-rg --xml
[xml]$xml = $publishXml
$ftpProfile = $xml.publishData.publishProfile | Where-Object { $_.publishMethod -eq 'FTP' }

$ftpUrl = $ftpProfile.publishUrl -replace 'ftps://', 'ftp://'
$ftpUser = $ftpProfile.userName
$ftpPass = $ftpProfile.userPWD

Write-Host "Connecting to $ftpUrl..."

# Create FTP request
$files = Get-ChildItem -Path "D:\mcl-site" -Recurse -File | 
    Where-Object { 
        $_.FullName -notmatch '\\venv\\' -and 
        $_.FullName -notmatch '\\media\\' -and
        $_.FullName -notmatch '\\.git\\' -and
        $_.FullName -notmatch '\\__pycache__\\' -and
        $_.Extension -ne '.pyc' -and
        $_.Extension -ne '.sqlite3'
    }

Write-Host "Found $($files.Count) files to upload"

foreach ($file in $files) {
    $relativePath = $file.FullName.Substring("D:\mcl-site".Length + 1) -replace '\\', '/'
    $uri = "$ftpUrl/site/wwwroot/$relativePath"
    
    Write-Host "Uploading: $relativePath"
    
    try {
        $request = [System.Net.FtpWebRequest]::Create($uri)
        $request.Credentials = New-Object System.Net.NetworkCredential($ftpUser, $ftpPass)
        $request.Method = [System.Net.WebRequestMethods+Ftp]::UploadFile
        $request.UseBinary = $true
        $request.EnableSsl = $true
        
        $fileContent = [System.IO.File]::ReadAllBytes($file.FullName)
        $request.ContentLength = $fileContent.Length
        
        $requestStream = $request.GetRequestStream()
        $requestStream.Write($fileContent, 0, $fileContent.Length)
        $requestStream.Close()
        
        $response = $request.GetResponse()
        $response.Close()
    }
    catch {
        Write-Host "Failed: $_" -ForegroundColor Red
    }
}

Write-Host "Upload complete!"
```

Then run:
```powershell
.\deploy-ftp.ps1
```

---

## 📊 Your Deployment Summary

**Site URL**: https://mcl-mk-site.azurewebsites.net
**Admin Username**: Create during `createsuperuser` step
**Database**: PostgreSQL (automatically connected)
**Media Storage**: Azure Blob Storage (automatically configured)

**Monthly Cost**: ~€30 (App + Database + Storage)

## 🆘 Troubleshooting

If site shows errors:
```powershell
# View live logs
az webapp log tail --name mcl-mk-site --resource-group mcl-site-rg

# Check app status
az webapp show --name mcl-mk-site --resource-group mcl-site-rg --query "state"
```
