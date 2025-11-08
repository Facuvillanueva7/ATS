# Deployment Playbook

1. Provision Azure resources with Bicep:
   ```bash
   az deployment group create \
     --resource-group rg-ats-dev \
     --template-file infra/bicep/main.bicep \
     --parameters environment=dev sqlAdminLogin=atsadmin sqlAdminPassword=Secret123!
   ```
2. Configure GitHub Actions secrets: `AZURE_CREDENTIALS`, `SQL_CONN_STRING`, `OPENAI_KEY`, `AZURE_STORAGE_CONNECTION_STRING`.
3. Pipeline stages:
   - Build & test backend (`dotnet test`).
   - Build & test frontend (`npm run test`).
   - Build & test ML (`pytest`).
   - Build container images and push to ACR.
   - Run database migrations.
   - Deploy containers to Azure Container Apps or AKS (TODO chart).
4. Validate health endpoints (`/health`, `/readiness`).
