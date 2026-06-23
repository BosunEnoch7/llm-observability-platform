targetScope = 'resourceGroup'

@description('Azure region used by the foundation deployment.')
param location string = resourceGroup().location

@description('Short workload name used in resource names.')
param workloadName string = 'llmobs'

@allowed([
  'dev'
  'staging'
  'prod'
])
param environmentName string = 'dev'

@description('Fully-qualified image reference in ACR.')
param containerImage string

@allowed([
  'simulated'
  'azure_openai'
])
param llmProvider string = 'simulated'

@description('Azure OpenAI account name from the foundation deployment.')
param azureOpenAIAccountName string = ''

@description('Azure OpenAI deployment name. Required when llmProvider is azure_openai.')
param azureOpenAIDeployment string = ''

@allowed([
  'disabled'
  'monitor'
  'enforce'
])
param safetyMode string = 'monitor'

param promptVersion string = 'v1'

var prefix = '${workloadName}-${environmentName}'
var suffix = uniqueString(subscription().id, location, workloadName, environmentName)
var acrName = toLower(replace('acr${workloadName}${environmentName}${suffix}', '-', ''))

resource environment 'Microsoft.App/managedEnvironments@2024-03-01' existing = {
  name: '${prefix}-cae'
}

resource identity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' existing = {
  name: '${prefix}-identity'
}

resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' existing = {
  name: acrName
}

resource containerApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: '${prefix}-api'
  location: location
  tags: {
    environment: environmentName
  }
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${identity.id}': {}
    }
  }
  properties: {
    managedEnvironmentId: environment.id
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: 8000
        transport: 'auto'
        allowInsecure: false
      }
      registries: [
        {
          server: acr.properties.loginServer
          identity: identity.id
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'llm-service'
          image: containerImage
          env: [
            {
              name: 'APP_ENV'
              value: environmentName
            }
            {
              name: 'LLM_PROVIDER'
              value: llmProvider
            }
            {
              name: 'AZURE_OPENAI_ENDPOINT'
              value: empty(azureOpenAIAccountName) ? '' : 'https://${azureOpenAIAccountName}.openai.azure.com'
            }
            {
              name: 'AZURE_OPENAI_DEPLOYMENT'
              value: azureOpenAIDeployment
            }
            {
              name: 'AZURE_USE_MANAGED_IDENTITY'
              value: 'true'
            }
            {
              name: 'PROMPT_VERSION'
              value: promptVersion
            }
            {
              name: 'SAFETY_MODE'
              value: safetyMode
            }
            {
              name: 'OTEL_ENABLED'
              value: 'false'
            }
          ]
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          probes: [
            {
              type: 'Liveness'
              httpGet: {
                path: '/health/live'
                port: 8000
                scheme: 'HTTP'
              }
              initialDelaySeconds: 10
              periodSeconds: 15
              timeoutSeconds: 5
              failureThreshold: 3
            }
            {
              type: 'Readiness'
              httpGet: {
                path: '/health/ready'
                port: 8000
                scheme: 'HTTP'
              }
              initialDelaySeconds: 5
              periodSeconds: 10
              timeoutSeconds: 5
              failureThreshold: 3
            }
          ]
        }
      ]
      scale: {
        minReplicas: environmentName == 'prod' ? 2 : 1
        maxReplicas: environmentName == 'prod' ? 10 : 3
        rules: [
          {
            name: 'http-concurrency'
            http: {
              metadata: {
                concurrentRequests: '50'
              }
            }
          }
        ]
      }
    }
  }
}

output containerAppName string = containerApp.name
output fqdn string = containerApp.properties.configuration.ingress.fqdn
output url string = 'https://${containerApp.properties.configuration.ingress.fqdn}'
