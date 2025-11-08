param namePrefix string
param location string

resource storage 'Microsoft.Storage/storageAccounts@2022-09-01' = {
  name: '${namePrefix}storage'
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    allowBlobPublicAccess: false
    minimumTlsVersion: 'TLS1_2'
  }
}

output storageAccountName string = storage.name
