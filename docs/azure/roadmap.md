# Azure deployment roadmap

The local stack is intentionally cloud-portable. The planned Azure production
architecture maps its components as follows:

| Local component | Azure target |
| --- | --- |
| FastAPI container | Azure Container Apps initially; AKS when Kubernetes control is justified |
| Local Docker image | Azure Container Registry |
| Environment secrets | Azure Key Vault with managed identity |
| Prometheus | Azure Monitor managed service for Prometheus |
| Grafana | Azure Managed Grafana |
| Alert routing | Azure Monitor action groups and/or retained Alertmanager routing |
| LLM provider | Azure OpenAI through managed identity where supported |
| GitHub Actions credentials | GitHub OIDC federation, without stored client secrets |

Infrastructure will be defined with Bicep or Terraform in a later phase. The
application will remain stateless, use health probes, emit bounded-cardinality
metrics, and receive all environment-specific configuration at runtime.
