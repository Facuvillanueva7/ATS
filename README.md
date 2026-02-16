# ATS Dashboard POC (Streamlit + Python)

POC **mostrable y funcional** de dashboard ATS hecho 100% en Python con Streamlit, data mock realista y motor de reglas administrable desde UI.

## Quickstart

```bash
pip install -r requirements.txt
streamlit run app.py
```

Abre el navegador en `http://localhost:8501`.

## Funcionalidades incluidas

### 1) Home / Dashboard
- KPIs: total candidates, new, in_progress, rejected, hired.
- Average time-to-hire.
- Funnel por etapa.
- Promedio de días por etapa.
- Incidencias por tipo.
- Tendencia semanal (creados/hired/rejected).

### 2) Candidates
- Tabla con filtros por búsqueda, status, etapa, recruiter, skill y salario.
- Detalle de candidato con header de datos principales + tags de skills.
- Pipeline timeline con `inDate`, `outDate`, `durationDays`, `notes`, `actor`.
- Logs/incidences con filtros por tipo y rango de fechas.
- Export CSV para actividades y pipeline.

### 3) Rules Admin
- CRUD completo de reglas desde UI (crear/editar/activar/desactivar/eliminar).
- Ejecución manual del engine con botón **Run rules**.
- Vista de alertas generadas.
- Auditoría de ejecuciones en `rule_runs`.
- Persistencia en SQLite (`ats_dashboard.db`) para `rules`, `alerts`, `rule_runs`.

## Mock data
- Generación automática con seed fija (default `42`) y botón de regeneración.
- Exactamente **60 candidatos**.
- Distribución de status:
  - 10 New
  - 25 In Progress
  - 15 Rejected
  - 10 Hired
- Skills variadas: SQL, SQLServer, .NET, C#, React, Angular, DevOps, ETL, Power BI, etc.
- Pipeline + actividades realistas por candidato.
- Incidencias incluidas: `delay`, `rejected_salary`, `missing_references`, `no_show`, `client_feedback`, `background_check`.

## Estructura del proyecto

```text
app.py
requirements.txt
src/
  charts/
    charts.py
  connectors/
    connector.py
  db/
    sqlite.py
  mock/
    generator.py
  models/
    schemas.py
  rules/
    engine.py
```

## Conectar API real luego

Se deja interfaz stub en `src/connectors/connector.py`:
- `fetch_candidates_from_api()`
- `fetch_pipeline_events_from_api()`
- `push_rule_to_api(rule_payload)`

Para migrar de mock a real:
1. Implementar llamadas reales en `connector.py`.
2. Mapear payload externo a los modelos Pydantic de `src/models/schemas.py`.
3. Reemplazar el loader de `app.py` para priorizar conector real y fallback a mock.
4. Mantener Rules Admin sobre SQLite o sincronizar reglas a backend vía `push_rule_to_api`.

## Notas
- No depende de APIs externas para funcionar.
- Todo es Python puro (sin frameworks JS).
