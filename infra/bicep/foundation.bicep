targetScope = 'subscription'

@description('Azure region for the platform resources.')
param location string = 'eastus2'

@description('Short workload name used in resource names.')
@minLength(3)
@maxLength(12)
param workloadName string = 'llmobs'

@description('Deployment environment name.')
@allowed([
  'dev'
  'staging'
  'prod'
])
param environmentName string = 'dev'

@description('Provision an Azure OpenAI account. Model availability is region-specific.')
param deployAzureOpenAI bool = false

@description('Provision Azure Monitor workspace and Azure Managed Grafana.')
param deployManagedObservability bool = true

var resourceGroupName = '${workloadName}-${environmentName}-rg'
var suffix = uniqueString(subscription().id, location, workloadName, environmentName)

resource resourceGroup 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: resourceGroupName
  location: location
  tags: {
    workload: workloadName
    environment: environmentName
    managedBy: 'bicep'
  }
}

module platform './modules/platform.bicep' = {
  name: 'platform-${environmentName}'
  scope: resourceGroup
  params: {
    location: location
    workloadName: workloadName
    environmentName: environmentName
    suffix: suffix
    deployAzureOpenAI: deployAzureOpenAI
    deployManagedObservability: deployManagedObservability
  }
}

output resourceGroupName string = resourceGroup.name
output acrName string = platform.outputs.acrName
output acrLoginServer string = platform.outputs.acrLoginServer
output containerAppsEnvironmentName string = platform.outputs.containerAppsEnvironmentName
output managedIdentityName string = platform.outputs.managedIdentityName
output keyVaultName string = platform.outputs.keyVaultName
output azureOpenAIAccountName string = platform.outputs.azureOpenAIAccountName
output azureOpenAIEndpoint string = platform.outputs.azureOpenAIEndpoint
output managedGrafanaEndpoint string = platform.outputs.managedGrafanaEndpoint
