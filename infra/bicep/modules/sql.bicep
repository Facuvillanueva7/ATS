param namePrefix string
param location string
param administratorLogin string
@secure()
param administratorPassword string

resource sqlServer 'Microsoft.Sql/servers@2022-02-01-preview' = {
  name: '${namePrefix}-sql'
  location: location
  properties: {
    administratorLogin: administratorLogin
    administratorLoginPassword: administratorPassword
    publicNetworkAccess: 'Disabled'
  }
}

resource database 'Microsoft.Sql/servers/databases@2022-02-01-preview' = {
  name: '${sqlServer.name}/core'
  properties: {
    zoneRedundant: false
  }
  sku: {
    name: 'GP_S_Gen5_2'
    tier: 'GeneralPurpose'
  }
}

output sqlServerName string = sqlServer.name
output databaseName string = database.name
