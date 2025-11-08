param namePrefix string
param location string

resource serviceBusNamespace 'Microsoft.ServiceBus/namespaces@2022-10-01-preview' = {
  name: '${namePrefix}-sb'
  location: location
  sku: {
    name: 'Standard'
    tier: 'Standard'
  }
  properties: {
    disableLocalAuth: true
  }
}

output namespaceName string = serviceBusNamespace.name
