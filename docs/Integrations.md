# Integrations Guide

- **Notion**: configure webhook secrets in Azure Key Vault (`notion-api-token`).
- **Make**: register endpoint `/api/integrations/make/webhook` and verify signature header `X-Make-Signature` (TODO handler).
- **Criteria**: push assessment results to `/api/integrations/criteria/results`.
- **Microsoft Teams**: use Azure AD app + webhook URL stored in Key Vault.
