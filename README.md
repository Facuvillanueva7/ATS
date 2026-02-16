# ATS Dashboard POC (Streamlit + Python)

POC **mostrable y funcional** de dashboard ATS hecho 100% en Python con Streamlit.
Ahora incluye una vista **Kanban** para candidatos "reales" persistidos en archivos JSON locales (sin DB).

## Quickstart

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Páginas
- Home / Dashboard
- Candidates
- Rules Admin
- **Kanban**

## Kanban (POC v1)
- Columnas configurables desde `src/config.py` (`KANBAN_COLUMNS`):
  - New
  - Tests - validations
  - HR Interview
  - Tech Interview
  - Hired
  - Rejected
  - Talent pool
- Cards con datos clave: name, role, recruiter, salary, english, hard/soft skills, days in process, application date.
- Filtros: search (name/email), recruiter, role, english_level.
- Movimiento de cards con fallback POC (`Move to` + `Move`).
- Add candidate desde UI (alta simple a New o Talent pool).
- Export CSV de candidatos reales.

## Persistencia JSON (gratis y liviana)
Archivos creados automáticamente en `/data`:
- `data/real_candidates.json`
- `data/real_activities.json`
- `data/rules.json`
- `data/alerts.json`
- `data/rule_runs.json`

Si no existen, se autoseedean:
- 20 candidatos realistas para Kanban.
- actividades vacías.
- reglas base para Rules Admin.

Cada movimiento en Kanban:
- actualiza `kanban_stage` y `updated_at` del candidato.
- registra una actividad `stage_change` en `real_activities.json`.
- persiste inmediatamente en disco.

## Data source toggle (Mock / Real)
En sidebar se puede alternar:
- **Mock**: usa generador mock (60 candidatos).
- **Real**: usa `real_candidates.json` y deriva KPIs/charts/tabla.

Para datos reales sin pipeline explícito, se construye una timeline mínima derivada de `kanban_stage`.

## Estructura

```text
app.py
requirements.txt
data/
src/
  config.py
  charts/
    charts.py
  connectors/
    connector.py
  mock/
    generator.py
  models/
    schemas.py
  rules/
    engine.py
  storage/
    json_store.py
  views/
    kanban.py
```

## Integración futura con API/DB
- Se mantiene `src/connectors/connector.py` como interfaz stub para APIs reales.
- Si más adelante se requiere SQLite, se puede agregar una capa de storage intercambiable sin romper la UI (actualmente JSON-first).
