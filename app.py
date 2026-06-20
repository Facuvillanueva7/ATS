from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from src.config import KANBAN_COLUMNS
from src.storage.json_store import load_activities, load_candidates, seed_if_missing
from src.views.kanban import render_kanban

st.set_page_config(page_title="Workpulse ATS", page_icon="◼", layout="wide")


def _candidate_table(candidates: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "ID": candidate.get("id"),
                "Nombre": candidate.get("name"),
                "Email": candidate.get("email"),
                "Vacante": candidate.get("role"),
                "Etapa": candidate.get("kanban_stage"),
                "Recruiter": candidate.get("recruiter"),
                "Días en proceso": candidate.get("days_in_process", 0),
                "Fecha de aplicación": candidate.get("application_date"),
            }
            for candidate in candidates
        ]
    )


def render_dashboard(candidates: list[dict]) -> None:
    st.header("Dashboard")
    st.caption("Salud operativa del pipeline desde la misma fuente persistida del Kanban.")

    counts = {stage: sum(c.get("kanban_stage") == stage for c in candidates) for stage in KANBAN_COLUMNS}
    blocked = sum(int(c.get("days_in_process", 0)) >= 14 for c in candidates)
    active = len(candidates) - counts.get("Contratado", 0) - counts.get("Rechazado", 0)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Candidatos", len(candidates))
    c2.metric("Procesos activos", active)
    c3.metric("Atascados +14 días", blocked)
    c4.metric("Contratados", counts.get("Contratado", 0))

    stage_df = pd.DataFrame({"Etapa": list(counts), "Candidatos": list(counts.values())})
    st.bar_chart(stage_df.set_index("Etapa"))

    st.subheader("Atención requerida")
    attention = [
        c for c in candidates
        if int(c.get("days_in_process", 0)) >= 14
        and c.get("kanban_stage") not in {"Contratado", "Rechazado"}
    ]
    if attention:
        st.dataframe(_candidate_table(attention), use_container_width=True, hide_index=True)
    else:
        st.success("No hay candidatos activos con más de 14 días en proceso.")


def render_candidates(candidates: list[dict]) -> None:
    st.header("Candidatos")
    st.caption("Listado y detalle desde data/real_candidates.json.")

    search = st.text_input("Buscar por nombre, email o vacante")
    stage = st.multiselect("Etapa", KANBAN_COLUMNS)

    filtered = candidates
    if search:
        query = search.lower().strip()
        filtered = [
            c for c in filtered
            if query in c.get("name", "").lower()
            or query in c.get("email", "").lower()
            or query in c.get("role", "").lower()
        ]
    if stage:
        filtered = [c for c in filtered if c.get("kanban_stage") in stage]

    table = _candidate_table(filtered)
    st.dataframe(table, use_container_width=True, hide_index=True)
    if not filtered:
        st.info("No hay candidatos con los filtros actuales.")
        return

    candidate_ids = [c["id"] for c in filtered]
    selected_id = st.selectbox(
        "Abrir candidato",
        candidate_ids,
        format_func=lambda value: next(c["name"] for c in filtered if c["id"] == value),
    )
    candidate = next(c for c in filtered if c["id"] == selected_id)

    st.subheader(candidate.get("name", "Sin nombre"))
    left, right = st.columns(2)
    with left:
        st.write(f"**Email:** {candidate.get('email', '-')}")
        st.write(f"**Vacante:** {candidate.get('role', '-')}")
        st.write(f"**Etapa:** {candidate.get('kanban_stage', '-')}")
        st.write(f"**Recruiter:** {candidate.get('recruiter', '-')}")
    with right:
        st.write(f"**Inglés:** {candidate.get('english_level', '-')}")
        st.write(f"**Expectativa salarial:** {candidate.get('salary_expectation', 0)}")
        st.write(f"**Aplicó:** {candidate.get('application_date', '-')}")
        st.write(f"**Días en proceso:** {candidate.get('days_in_process', 0)}")

    st.write("**Hard skills:**", ", ".join(candidate.get("hard_skills", [])) or "-")
    st.write("**Soft skills:**", ", ".join(candidate.get("soft_skills", [])) or "-")

    activities = [a for a in load_activities() if str(a.get("candidate_id")) == str(selected_id)]
    st.subheader("Actividad")
    if activities:
        st.dataframe(pd.DataFrame(activities), use_container_width=True, hide_index=True)
    else:
        st.info("Todavía no hay actividad registrada para este candidato.")


def main() -> None:
    seed_if_missing()
    candidates = load_candidates()

    st.sidebar.title("Workpulse")
    st.sidebar.caption(f"Última apertura: {date.today().isoformat()}")
    page = st.sidebar.radio("Navegación", ["Dashboard", "Kanban", "Candidatos"])

    if page == "Dashboard":
        render_dashboard(candidates)
    elif page == "Kanban":
        render_kanban()
    else:
        render_candidates(candidates)


if __name__ == "__main__":
    main()
