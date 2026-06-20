from __future__ import annotations

from datetime import datetime

import pandas as pd
import streamlit as st

from src.config import DEFAULT_NEW_STAGE, KANBAN_COLUMNS
from src.storage.json_store import add_candidate, load_candidates, seed_candidates, update_candidate_stage


def _filter_candidates(candidates: list[dict]) -> list[dict]:
    st.subheader("Filtros")
    c1, c2, c3 = st.columns(3)
    with c1:
        search = st.text_input("Buscar por nombre o email")
    with c2:
        recruiters = sorted({c.get("recruiter", "") for c in candidates if c.get("recruiter")})
        recruiter = st.selectbox("Recruiter", options=["Todos"] + recruiters)
    with c3:
        roles = sorted({c.get("role", "") for c in candidates if c.get("role")})
        role = st.selectbox("Vacante", options=["Todas"] + roles)

    filtered = candidates
    if search:
        query = search.lower().strip()
        filtered = [c for c in filtered if query in c.get("name", "").lower() or query in c.get("email", "").lower()]
    if recruiter != "Todos":
        filtered = [c for c in filtered if c.get("recruiter") == recruiter]
    if role != "Todas":
        filtered = [c for c in filtered if c.get("role") == role]
    return filtered


def _candidate_card(candidate: dict) -> None:
    with st.container(border=True):
        st.markdown(f"**{candidate.get('name', 'Sin nombre')}**")
        st.caption(f"{candidate.get('role', 'Sin vacante')} · {candidate.get('recruiter', 'Sin asignar')}")
        st.write(f"Inglés: {candidate.get('english_level', '-')}")
        st.write(f"Días: {candidate.get('days_in_process', 0)}")
        skills = ", ".join(candidate.get("hard_skills", []))
        if skills:
            st.caption(skills)

        current_stage = candidate.get("kanban_stage", DEFAULT_NEW_STAGE)
        new_stage = st.selectbox(
            "Mover a",
            options=KANBAN_COLUMNS,
            key=f"move_{candidate['id']}",
            index=KANBAN_COLUMNS.index(current_stage) if current_stage in KANBAN_COLUMNS else 0,
        )
        if st.button("Guardar movimiento", key=f"move_btn_{candidate['id']}", use_container_width=True):
            if new_stage == current_stage:
                st.info("El candidato ya está en esa etapa.")
            else:
                update_candidate_stage(candidate["id"], new_stage, actor="recruiter")
                st.success(f"{candidate['name']} movido a {new_stage}")
                st.rerun()


def render_kanban() -> None:
    st.header("Kanban")
    st.caption("Pipeline operativo persistido en JSON.")

    candidates = load_candidates()
    top1, top2, top3 = st.columns(3)
    with top1:
        df = pd.DataFrame(candidates)
        st.download_button(
            "Exportar CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="workpulse_candidates.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with top2:
        if st.button("Restaurar 20 candidatos demo", use_container_width=True):
            seed_candidates(20)
            st.success("Datos demo restaurados.")
            st.rerun()
    with top3:
        with st.popover("Agregar candidato", use_container_width=True):
            with st.form("add_candidate_form"):
                name = st.text_input("Nombre")
                email = st.text_input("Email")
                role = st.text_input("Vacante")
                recruiter = st.text_input("Recruiter")
                english_level = st.selectbox("Inglés", ["A2", "B1", "B2", "C1", "C2"])
                salary = st.number_input("Expectativa salarial", min_value=0, value=25000)
                hard = st.text_input("Hard skills separadas por coma")
                soft = st.text_input("Soft skills separadas por coma")
                stage = st.selectbox("Etapa inicial", KANBAN_COLUMNS)
                submit = st.form_submit_button("Crear")
                if submit:
                    if not name.strip() or not email.strip():
                        st.error("Nombre y email son obligatorios.")
                    else:
                        add_candidate({
                            "name": name.strip(),
                            "email": email.strip(),
                            "role": role.strip() or "Sin definir",
                            "position": role.strip() or "General",
                            "recruiter": recruiter.strip() or "Sin asignar",
                            "english_level": english_level,
                            "salary_expectation": salary,
                            "hard_skills": [x.strip() for x in hard.split(",") if x.strip()],
                            "soft_skills": [x.strip() for x in soft.split(",") if x.strip()],
                            "application_date": datetime.now().date().isoformat(),
                            "days_in_process": 0,
                            "kanban_stage": stage,
                        })
                        st.success("Candidato creado.")
                        st.rerun()

    filtered = _filter_candidates(candidates)
    tabs = st.tabs(KANBAN_COLUMNS)
    for tab, stage in zip(tabs, KANBAN_COLUMNS):
        with tab:
            stage_cards = [c for c in filtered if c.get("kanban_stage") == stage]
            st.caption(f"{len(stage_cards)} candidatos")
            if not stage_cards:
                st.info("Sin candidatos en esta etapa.")
            for candidate in stage_cards:
                _candidate_card(candidate)
