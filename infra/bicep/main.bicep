param environment string = 'dev'
param location string = resourceGroup().location
param sqlAdminLogin string
@secure()
param sqlAdminPassword string

var namePrefix = 'orion-ats-${environment}'

module storage 'modules/storage.bicep' = {
  name: 'storage'
  params: {
    namePrefix: namePrefix
    location: location
  }
}

module sql 'modules/sql.bicep' = {
  name: 'sql'
  params: {
    namePrefix: namePrefix
    location: location
    administratorLogin: sqlAdminLogin
    administratorPassword: sqlAdminPassword
  }
}

module serviceBus 'modules/servicebus.bicep' = {
  name: 'servicebus'
  params: {
    namePrefix: namePrefix
    location: location
  }
}

module appInsights 'modules/appinsights.bicep' = {
  name: 'appinsights'
  params: {
    namePrefix: namePrefix
    location: location
  }
}

output storageAccountName string = storage.outputs.storageAccountName
output sqlServerName string = sql.outputs.sqlServerName
output serviceBusNamespace string = serviceBus.outputs.namespaceName
output applicationInsightsName string = appInsights.outputs.appInsightsName
