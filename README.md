# Orion ATS Platform

Enterprise-grade applicant tracking system with AI-assisted screening, predictive analytics and full ATS workflows.

## Monorepo structure
- `backend/`: ASP.NET Core Minimal API, EF Core, integrations.
- `ml-service/`: FastAPI service for parsing, embeddings, matching and predictive models.
- `frontend/`: React 18 + Vite admin interface.
- `infra/`: Azure Bicep modules.
- `ops/`: Deployment automation stubs.
- `seeds/`: Synthetic data and CV examples (TODO).
- `docs/`: Architecture and runbooks.

## Getting started
1. Install prerequisites: Docker, .NET 8 SDK, Node.js 18+, Python 3.11.
2. Copy `.env.sample` to `.env` (TODO) and set secrets.
3. Run database migrations: `dotnet ef database update` (from `backend`).
4. Launch dev stack: `docker compose up` (includes RabbitMQ as the local Service Bus alternative).
5. Frontend dev server: `npm install && npm run dev` (from `frontend`).
6. ML service tests: `poetry install && pytest` (from `ml-service`).
7. Track experiments: `poetry run mlflow ui`.

See `docs/` for detailed guides.
