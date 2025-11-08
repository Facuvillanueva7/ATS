# Infra

Bicep templates to provision core Azure resources. See `bicep/main.bicep` for the entry point.

## Variables
- `environment`: Deployment slot (dev/stg/prod).
- `location`: Azure region (e.g. westeurope).
- `sqlAdminLogin` / `sqlAdminPassword`: SQL admin credentials.
- `openAiEndpoint` / `openAiKey`: Optional for Azure OpenAI.
