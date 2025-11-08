# Dev Runbook

## Local stack
1. Start databases and services:
   ```bash
   docker compose up
   ```
2. Apply EF Core migrations:
   ```bash
   cd backend
   dotnet ef database update
   ```
3. Launch ML service standalone for debugging:
   ```bash
   cd ml-service
   poetry install
   poetry run uvicorn app.main:app --reload --port 8081
   ```
4. Start frontend:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Training models
```bash
cd ml-service
poetry run pytest
poetry run mlflow ui
```

## Integrations
- Configure Azure OpenAI + fallback local embeddings via environment variables `EMBEDDINGS_PROVIDER`.
- Secrets are stored in Azure Key Vault (see `infra/bicep/main.bicep`).
