targetScope = 'resourceGroup'

param location string
@minLength(3)
@maxLength(12)
param workloadName string
@minLength(3)
@allowed([
  'dev'
  'staging'
  'prod'
])
param environmentName string
@minLength(13)
param suffix string
param deployAzureOpenAI bool
param deployManagedObservability bool

var prefix = '${workloadName}-${environmentName}'
var acrName = toLower(replace('acr${workloadName}${environmentName}${suffix}', '-', ''))
var keyVaultName = take(toLower('${workloadName}-${environmentName}-${suffix}'), 24)
var openAIAccountName = take(toLower('${workloadName}-${environmentName}-aoai-${suffix}'), 64)

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: '${prefix}-logs'
  location: location
  tags: {
    environment: environmentName
  }
  properties: {
    retentionInDays: 30
    features: {
      enableLogAccessUsingOnlyResourcePermissions: true
    }
  }
}

resource identity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: '${prefix}-identity'
  location: location
  tags: {
    environment: environmentName
  }
}

resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: acrName
  location: location
  tags: {
    environment: environmentName
  }
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: false
    publicNetworkAccess: 'Enabled'
  }
}

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultName
  location: location
  tags: {
    environment: environmentName
  }
  properties: {
    tenantId: subscription().tenantId
    sku: {
      family: 'A'
      name: 'standard'
    }
    enableRbacAuthorization: true
    enablePurgeProtection: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 90
    publicNetworkAccess: 'Enabled'
  }
}

resource containerAppsEnvironment 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: '${prefix}-cae'
  location: location
  tags: {
    environment: environmentName
  }
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalytics.properties.customerId
        sharedKey: logAnalytics.listKeys().primarySharedKey
      }
    }
    zoneRedundant: false
  }
}

resource azureOpenAI 'Microsoft.CognitiveServices/accounts@2024-10-01' = if (deployAzureOpenAI) {
  name: openAIAccountName
  location: location
  tags: {
    environment: environmentName
  }
  kind: 'OpenAI'
  sku: {
    name: 'S0'
  }
  properties: {
    customSubDomainName: openAIAccountName
    disableLocalAuth: true
    publicNetworkAccess: 'Enabled'
    networkAcls: {
      defaultAction: 'Allow'
    }
  }
}

resource monitorWorkspace 'Microsoft.Monitor/accounts@2023-04-03' = if (deployManagedObservability) {
  name: '${prefix}-monitor'
  location: location
  tags: {
    environment: environmentName
  }
  properties: {}
}

resource managedGrafana 'Microsoft.Dashboard/grafana@2023-09-01' = if (deployManagedObservability) {
  name: '${prefix}-grafana-${suffix}'
  location: location
  tags: {
    environment: environmentName
  }
  sku: {
    name: 'Standard'
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    apiKey: 'Disabled'
    deterministicOutboundIP: 'Enabled'
    publicNetworkAccess: 'Enabled'
    grafanaIntegrations: {
      azureMonitorWorkspaceIntegrations: [
        {
          azureMonitorWorkspaceResourceId: monitorWorkspace.id
        }
      ]
    }
  }
}

resource acrPull 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(acr.id, identity.id, 'acr-pull')
  scope: acr
  properties: {
    principalId: identity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '7f951dda-4ed3-4680-a7ca-43fe172d538d'
    )
  }
}

resource keyVaultSecretsUser 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(keyVault.id, identity.id, 'key-vault-secrets-user')
  scope: keyVault
  properties: {
    principalId: identity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '4633458b-17de-408a-b874-0445c86b69e6'
    )
  }
}

resource azureOpenAIUser 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (deployAzureOpenAI) {
  name: guid(azureOpenAI.id, identity.id, 'cognitive-services-openai-user')
  scope: azureOpenAI
  properties: {
    principalId: identity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd'
    )
  }
}

output acrName string = acr.name
output acrLoginServer string = acr.properties.loginServer
output containerAppsEnvironmentName string = containerAppsEnvironment.name
output managedIdentityName string = identity.name
output keyVaultName string = keyVault.name
output azureOpenAIAccountName string = azureOpenAI.?name ?? ''
output azureOpenAIEndpoint string = azureOpenAI.?properties.endpoint ?? ''
output managedGrafanaEndpoint string = managedGrafana.?properties.endpoint ?? ''
