# Azure deployment roadmap

The local stack is intentionally cloud-portable. The Azure production
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

The first infrastructure path is now defined with Bicep in `infra/bicep/`, and
GitHub Actions includes an OIDC-based deployment workflow. The application
remains stateless, uses health probes, emits bounded-cardinality metrics, and
receives all environment-specific configuration at runtime.

## Promotion path

1. Run local validation and screenshot evidence.
2. Configure GitHub environments and Azure federated identity.
3. Run Bicep `what-if` against the target subscription.
4. Deploy the foundation and app workflow to `dev`.
5. Validate `/health/ready`, metrics, logs, and dashboard access.
6. Promote to `staging` and `prod` only with approval, budgets, and rollback
   ownership.
