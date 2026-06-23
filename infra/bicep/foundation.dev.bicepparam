using './foundation.bicep'

param location = 'eastus2'
param workloadName = 'llmobs'
param environmentName = 'dev'
param deployAzureOpenAI = false
param deployManagedObservability = true
