# ==============================================
# Azure Infrastructure as Code (Bicep)
# ==============================================
# Deploy with: az deployment group create --resource-group <rg-name> --template-file azure/main.bicep
# ==============================================

@description('The name of the web app')
param webAppName string = 'mcl-mk'

@description('Location for all resources')
param location string = resourceGroup().location

@description('The SKU of App Service Plan')
param sku string = 'B1'

@description('PostgreSQL admin username')
param postgresAdminLogin string = 'mcladmin'

@description('PostgreSQL admin password')
@secure()
param postgresAdminPassword string

@description('Django secret key')
@secure()
param djangoSecretKey string

// Variables
var appServicePlanName = '${webAppName}-plan'
var postgresServerName = '${webAppName}-postgres'
var storageAccountName = replace('${webAppName}storage', '-', '')

// App Service Plan
resource appServicePlan 'Microsoft.Web/serverfarms@2022-09-01' = {
  name: appServicePlanName
  location: location
  sku: {
    name: sku
    capacity: 1
  }
  kind: 'linux'
  properties: {
    reserved: true
  }
}

// Web App
resource webApp 'Microsoft.Web/sites@2022-09-01' = {
  name: webAppName
  location: location
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      appCommandLine: 'bash startup.sh'
      alwaysOn: sku != 'F1'
      ftpsState: 'Disabled'
      http20Enabled: true
    }
    httpsOnly: true
  }
}

// Web App Settings
resource webAppSettings 'Microsoft.Web/sites/config@2022-09-01' = {
  parent: webApp
  name: 'appsettings'
  properties: {
    DJANGO_SETTINGS_MODULE: 'mcl_site.settings.production'
    SECRET_KEY: djangoSecretKey
    DATABASE_URL: 'postgres://${postgresAdminLogin}:${postgresAdminPassword}@${postgresServer.properties.fullyQualifiedDomainName}:5432/mcl_db?sslmode=require'
    AZURE_ACCOUNT_NAME: storageAccount.name
    AZURE_ACCOUNT_KEY: storageAccount.listKeys().keys[0].value
    AZURE_CONTAINER: 'media'
    SCM_DO_BUILD_DURING_DEPLOYMENT: 'true'
    WEBSITE_HTTPLOGGING_RETENTION_DAYS: '7'
  }
}

// PostgreSQL Flexible Server
resource postgresServer 'Microsoft.DBforPostgreSQL/flexibleServers@2022-12-01' = {
  name: postgresServerName
  location: location
  sku: {
    name: 'Standard_B1ms'
    tier: 'Burstable'
  }
  properties: {
    version: '15'
    administratorLogin: postgresAdminLogin
    administratorLoginPassword: postgresAdminPassword
    storage: {
      storageSizeGB: 32
    }
    backup: {
      backupRetentionDays: 7
      geoRedundantBackup: 'Disabled'
    }
  }
}

// PostgreSQL Database
resource postgresDatabase 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2022-12-01' = {
  parent: postgresServer
  name: 'mcl_db'
  properties: {
    charset: 'UTF8'
    collation: 'uk_UA.utf8'
  }
}

// PostgreSQL Firewall Rule (Allow Azure Services)
resource postgresFirewallRule 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2022-12-01' = {
  parent: postgresServer
  name: 'AllowAzureServices'
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
}

// Storage Account for Media Files
resource storageAccount 'Microsoft.Storage/storageAccounts@2022-09-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: true
  }
}

// Blob Container for Media
resource blobContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2022-09-01' = {
  name: '${storageAccount.name}/default/media'
  properties: {
    publicAccess: 'Blob'
  }
}

// Outputs
output webAppUrl string = 'https://${webApp.properties.defaultHostName}'
output storageAccountName string = storageAccount.name
output postgresServerFqdn string = postgresServer.properties.fullyQualifiedDomainName
