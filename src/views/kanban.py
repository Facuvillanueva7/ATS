from __future__ import annotations

from datetime import datetime

import pandas as pd
import streamlit as st

from src.config import DEFAULT_NEW_STAGE, DEFAULT_POOL_STAGE, KANBAN_COLUMNS
from src.storage.json_store import add_candidate, load_candidates, update_candidate_stage


def _filter_candidates(candidates: list[dict]) -> list[dict]:
    st.subheader("Kanban filters")
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        search = st.text_input("Search (name/email)")
    with c2:
        recruiters = sorted({c.get("recruiter", "") for c in candidates})
        recruiter = st.selectbox("Recruiter", options=["All"] + recruiters)
    with c3:
        roles = sorted({c.get("role", "") for c in candidates})
        role = st.selectbox("Role", options=["All"] + roles)
    with c4:
        levels = sorted({c.get("english_level", "") for c in candidates})
        english = st.selectbox("English", options=["All"] + levels)

    filtered = candidates
    if search:
        query = search.lower().strip()
        filtered = [
            c for c in filtered if query in c.get("name", "").lower() or query in c.get("email", "").lower()
        ]
    if recruiter != "All":
        filtered = [c for c in filtered if c.get("recruiter") == recruiter]
    if role != "All":
        filtered = [c for c in filtered if c.get("role") == role]
    if english != "All":
        filtered = [c for c in filtered if c.get("english_level") == english]
    return filtered


def _candidate_card(candidate: dict):
    skills_hard = " ".join([f"`{s}`" for s in candidate.get("hard_skills", [])])
    skills_soft = " ".join([f"`{s}`" for s in candidate.get("soft_skills", [])])

    with st.container(border=True):
        st.markdown(f"### {candidate.get('name', 'N/A')}")
        st.caption(f"{candidate.get('role', 'N/A')} • Recruiter: {candidate.get('recruiter', 'N/A')}")
        st.write(f"💰 Salary: {candidate.get('salary_expectation', 0)}")
        st.write(f"🗣️ English: {candidate.get('english_level', 'N/A')}")
        st.markdown(f"**Hard skills:** {skills_hard if skills_hard else '-'}")
        st.markdown(f"**Soft skills:** {skills_soft if skills_soft else '-'}")
        st.write(f"⏱️ Days in process: {candidate.get('days_in_process', 0)}")
        st.write(f"📅 Application: {candidate.get('application_date', 'N/A')}")

        new_stage = st.selectbox(
            "Move to",
            options=KANBAN_COLUMNS,
            key=f"move_{candidate['id']}",
            index=KANBAN_COLUMNS.index(candidate.get("kanban_stage", DEFAULT_NEW_STAGE)),
        )
        if st.button("Move", key=f"move_btn_{candidate['id']}") and new_stage != candidate.get("kanban_stage"):
            update_candidate_stage(candidate["id"], new_stage, actor="system")
            st.success(f"Moved {candidate['name']} to {new_stage}")
            st.rerun()


def render_kanban() -> None:
    st.header("Kanban")
    st.caption("Dark board, cards con chips y persistencia JSON en /data")

    candidates = load_candidates()
    if not candidates:
        st.warning("No real candidates found.")
        return

    top1, top2 = st.columns([1, 1])
    with top1:
        df = pd.DataFrame(candidates)
        st.download_button(
            "Export CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="real_candidates.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with top2:
        with st.popover("Add candidate", use_container_width=True):
            with st.form("add_candidate_form"):
                name = st.text_input("Name")
                email = st.text_input("Email")
                role = st.text_input("Role")
                recruiter = st.text_input("Recruiter")
                english_level = st.selectbox("English", ["A2", "B1", "B2", "C1", "C2"])
                salary = st.number_input("Salary expectation", min_value=0, value=25000)
                hard = st.text_input("Hard skills (comma-separated)")
                soft = st.text_input("Soft skills (comma-separated)")
                stage = st.selectbox("Initial stage", [DEFAULT_NEW_STAGE, DEFAULT_POOL_STAGE])
                submit = st.form_submit_button("Create")
                if submit:
                    if not name or not email:
                        st.error("Name and email are required")
                    else:
                        add_candidate(
                            {
                                "name": name,
                                "email": email,
                                "role": role,
                                "position": role,
                                "recruiter": recruiter,
                                "english_level": english_level,
                                "salary_expectation": salary,
                                "hard_skills": [x.strip() for x in hard.split(",") if x.strip()],
                                "soft_skills": [x.strip() for x in soft.split(",") if x.strip()],
                                "application_date": datetime.now().date().isoformat(),
                                "days_in_process": 0,
                                "kanban_stage": stage,
                            }
                        )
                        st.success("Candidate added")
                        st.rerun()

    filtered = _filter_candidates(candidates)
    st.markdown("<style>.stApp { background-color: #0e1117; color: #fafafa; }</style>", unsafe_allow_html=True)

    columns = st.columns(len(KANBAN_COLUMNS))
    for idx, stage in enumerate(KANBAN_COLUMNS):
        with columns[idx]:
            st.markdown(f"## {stage}")
            stage_cards = [c for c in filtered if c.get("kanban_stage") == stage]
            st.caption(f"{len(stage_cards)} candidates")
            for candidate in stage_cards:
                _candidate_card(candidate)
