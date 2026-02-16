from __future__ import annotations

import json
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st

from src.charts.charts import (
    avg_days_per_stage_chart,
    funnel_chart,
    incidences_by_type_chart,
    weekly_trend_chart,
)
from src.config import KANBAN_COLUMNS
from src.mock.generator import generate_mock_candidates
from src.models.schemas import Activity, Candidate, PipelineStage, Rule
from src.rules.engine import run_rules
from src.storage.json_store import (
    add_rule,
    append_alerts,
    append_rule_run,
    delete_rule,
    load_activities,
    load_alerts,
    load_candidates,
    load_rule_runs,
    load_rules,
    seed_if_missing,
    update_rule,
)
from src.views.kanban import render_kanban

st.set_page_config(page_title="ATS Dashboard POC", layout="wide")


@st.cache_data(show_spinner=False)
def load_mock_data(seed: int):
    return generate_mock_candidates(seed=seed, n=60)


def _stage_to_status(stage: str) -> str:
    mapping = {
        "New": "New",
        "Hired": "Hired",
        "Rejected": "Rejected",
        "Talent pool": "In Progress",
        "Tests - validations": "In Progress",
        "HR Interview": "In Progress",
        "Tech Interview": "In Progress",
    }
    return mapping.get(stage, "In Progress")


def _build_real_pipeline(application_date: str, current_stage: str, recruiter: str) -> list[PipelineStage]:
    stage_order = [s for s in KANBAN_COLUMNS if s != "Talent pool"]
    if current_stage not in stage_order:
        current_stage = "New"
    idx = stage_order.index(current_stage)

    base = datetime.fromisoformat(application_date)
    pipeline = []
    for i, stage in enumerate(stage_order[: idx + 1]):
        in_date = base + timedelta(days=i * 3)
        out_date = None if i == idx else in_date + timedelta(days=2)
        pipeline.append(
            PipelineStage(
                name=stage,
                in_date=in_date,
                out_date=out_date,
                duration_days=(2 if out_date else None),
                notes="Derived timeline from kanban stage",
                actor=recruiter,
            )
        )
    return pipeline


def _real_to_candidate_model(records: list[dict], activities: list[dict]) -> list[Candidate]:
    by_id: dict[str, list[dict]] = {}
    for activity in activities:
        by_id.setdefault(str(activity.get("candidate_id")), []).append(activity)

    models = []
    for rec in records:
        stage = rec.get("kanban_stage", "New")
        status = _stage_to_status(stage)
        created_at = datetime.fromisoformat(rec.get("application_date", date.today().isoformat()))

        candidate_activities = []
        for item in by_id.get(str(rec.get("id")), []):
            ts = datetime.fromisoformat(item["timestamp"])
            candidate_activities.append(
                Activity(
                    timestamp=ts,
                    type=item.get("type", "stage_change"),
                    summary=item.get("summary", "Stage updated"),
                    actor=item.get("actor", "system"),
                    stage=item.get("to_stage", stage),
                )
            )

        models.append(
            Candidate(
                id=int(rec["id"]) if str(rec["id"]).isdigit() else abs(hash(str(rec["id"]))) % 10_000_000,
                name=rec.get("name", "N/A"),
                role=rec.get("role") or rec.get("position", "N/A"),
                country="N/A",
                email=rec.get("email", "N/A"),
                phone="N/A",
                salary=int(rec.get("salary_expectation", 0)),
                status=status,
                recruiter=rec.get("recruiter", "N/A"),
                skills=rec.get("hard_skills", []),
                created_at=created_at,
                hired_at=(datetime.fromisoformat(rec["updated_at"]) if stage == "Hired" else None),
                rejected_at=(datetime.fromisoformat(rec["updated_at"]) if stage == "Rejected" else None),
                pipeline=_build_real_pipeline(rec.get("application_date", date.today().isoformat()), stage, rec.get("recruiter", "system")),
                activities=candidate_activities,
            )
        )
    return models


def candidates_to_table(candidates):
    return pd.DataFrame(
        [
            {
                "id": c.id,
                "name": c.name,
                "email": c.email,
                "role": c.role,
                "status": c.status,
                "stage": c.pipeline[-1].name if c.pipeline else "N/A",
                "recruiter": c.recruiter,
                "salary": c.salary,
                "skills": ", ".join(c.skills),
                "country": c.country,
                "created_at": c.created_at,
            }
            for c in candidates
        ]
    )


def render_dashboard(candidates):
    st.header("Home / Dashboard")
    if not candidates:
        st.warning("No candidates available for selected data source.")
        return

    statuses = pd.Series([c.status for c in candidates]).value_counts()
    total = len(candidates)
    hired = int(statuses.get("Hired", 0))
    rejected = int(statuses.get("Rejected", 0))
    in_progress = int(statuses.get("In Progress", 0))
    new = int(statuses.get("New", 0))

    tth_values = [(c.hired_at - c.created_at).days for c in candidates if c.hired_at and c.hired_at >= c.created_at]
    avg_tth = sum(tth_values) / len(tth_values) if tth_values else 0

    cols = st.columns(6)
    for col, (label, value) in zip(
        cols,
        [
            ("Total candidates", total),
            ("New", new),
            ("In progress", in_progress),
            ("Rejected", rejected),
            ("Hired", hired),
            ("Avg time-to-hire", f"{avg_tth:.1f} days"),
        ],
    ):
        col.metric(label, value)

    c1, c2 = st.columns(2)
    c1.plotly_chart(funnel_chart(candidates), use_container_width=True)
    c2.plotly_chart(avg_days_per_stage_chart(candidates), use_container_width=True)

    c3, c4 = st.columns(2)
    c3.plotly_chart(incidences_by_type_chart(candidates), use_container_width=True)
    c4.plotly_chart(weekly_trend_chart(candidates), use_container_width=True)


def render_candidates(candidates):
    st.header("Candidates")
    table = candidates_to_table(candidates)
    if table.empty:
        st.warning("No candidates available.")
        return

    with st.expander("Filters", expanded=True):
        search = st.text_input("Search by name/email")
        status = st.multiselect("Status", sorted(table["status"].unique()))
        stage = st.multiselect("Stage", sorted(table["stage"].unique()))
        recruiter = st.multiselect("Recruiter", sorted(table["recruiter"].unique()))
        all_skills = sorted({skill for c in candidates for skill in c.skills})
        skill = st.multiselect("Skill", all_skills)
        salary_min, salary_max = st.slider(
            "Salary range",
            int(table["salary"].min()),
            int(table["salary"].max()),
            (int(table["salary"].min()), int(table["salary"].max())),
        )

    filtered = table.copy()
    if search:
        filtered = filtered[
            filtered["name"].str.contains(search, case=False, na=False)
            | filtered["email"].str.contains(search, case=False, na=False)
        ]
    if status:
        filtered = filtered[filtered["status"].isin(status)]
    if stage:
        filtered = filtered[filtered["stage"].isin(stage)]
    if recruiter:
        filtered = filtered[filtered["recruiter"].isin(recruiter)]
    if skill:
        filtered = filtered[filtered["skills"].apply(lambda x: any(s in x.split(", ") for s in skill))]
    filtered = filtered[(filtered["salary"] >= salary_min) & (filtered["salary"] <= salary_max)]

    st.dataframe(filtered, use_container_width=True, hide_index=True)
    if filtered.empty:
        st.info("No candidates found with current filters.")
        return

    selected_id = st.selectbox("Select candidate", options=filtered["id"].tolist())
    candidate = next(c for c in candidates if c.id == selected_id)

    st.markdown(
        f"""**{candidate.name}** — {candidate.role}  
📍 {candidate.country} | ✉️ {candidate.email} | 📞 {candidate.phone}  
💰 Salary: {candidate.salary} | 👤 Recruiter: {candidate.recruiter}  
🏷️ Skills: {", ".join(candidate.skills)}"""
    )

    p_df = pd.DataFrame(
        [
            {
                "stage": p.name,
                "inDate": p.in_date,
                "outDate": p.out_date,
                "durationDays": p.duration_days,
                "notes": p.notes,
                "actor": p.actor,
            }
            for p in candidate.pipeline
        ]
    )
    a_df = pd.DataFrame(
        [
            {"timestamp": a.timestamp, "type": a.type, "summary": a.summary, "actor": a.actor, "stage": a.stage}
            for a in candidate.activities
        ]
    )

    t1, t2 = st.tabs(["Pipeline Timeline", "Logs / Incidences"])
    with t1:
        st.dataframe(p_df, use_container_width=True, hide_index=True)
        st.download_button("Export pipeline CSV", p_df.to_csv(index=False).encode("utf-8"), f"candidate_{candidate.id}_pipeline.csv", "text/csv")
    with t2:
        if a_df.empty:
            st.info("No logs for this candidate")
        else:
            selected_types = st.multiselect("Type", options=sorted(a_df["type"].unique()))
            start_default = a_df["timestamp"].min().date()
            end_default = a_df["timestamp"].max().date()
            date_range = st.date_input("Date range", value=(start_default, end_default))
            logs = a_df.copy()
            if selected_types:
                logs = logs[logs["type"].isin(selected_types)]
            if isinstance(date_range, tuple) and len(date_range) == 2:
                logs = logs[(logs["timestamp"].dt.date >= date_range[0]) & (logs["timestamp"].dt.date <= date_range[1])]
            st.dataframe(logs, use_container_width=True, hide_index=True)
            st.download_button("Export activities CSV", logs.to_csv(index=False).encode("utf-8"), f"candidate_{candidate.id}_activities.csv", "text/csv")


def render_rules_admin(candidates):
    st.header("Rules Admin")
    rules = load_rules()

    with st.expander("Create rule"):
        with st.form("create_rule"):
            name = st.text_input("Name")
            description = st.text_area("Description")
            is_active = st.checkbox("Active", value=True)
            scope = st.selectbox("Scope", ["candidate", "pipeline", "activity"])
            condition_str = st.text_area("Condition JSON", '{"status":"Rejected","salary_gte":50000}')
            action_str = st.text_area("Action JSON", '{"message":"Rule triggered"}')
            severity = st.selectbox("Severity", ["low", "medium", "high", "critical"])
            if st.form_submit_button("Create"):
                try:
                    add_rule(
                        {
                            "name": name,
                            "description": description,
                            "is_active": is_active,
                            "scope": scope,
                            "condition": json.loads(condition_str),
                            "action": json.loads(action_str),
                            "severity": severity,
                        }
                    )
                    st.success("Rule created")
                    st.rerun()
                except json.JSONDecodeError:
                    st.error("Invalid JSON")

    for rule in rules:
        with st.container(border=True):
            st.markdown(f"**#{rule['id']} - {rule['name']}**")
            st.caption(f"Scope: {rule['scope']} | Severity: {rule['severity']} | Active: {rule['is_active']}")
            c1, c2 = st.columns(2)
            if c1.button(f"Toggle #{rule['id']}"):
                updated = dict(rule)
                updated["is_active"] = not updated["is_active"]
                update_rule(rule["id"], updated)
                st.rerun()
            if c2.button(f"Delete #{rule['id']}"):
                delete_rule(rule["id"])
                st.rerun()

    if st.button("Run rules engine", type="primary"):
        active = [Rule(**r) for r in load_rules() if r.get("is_active")]
        alerts = run_rules(candidates, active)
        alert_payloads = [a.model_dump(mode="json") for a in alerts]
        append_alerts(alert_payloads)
        append_rule_run(
            {
                "run_at": datetime.now().isoformat(),
                "rules_evaluated": len(active),
                "alerts_generated": len(alerts),
                "triggered_by": "streamlit-admin",
            }
        )
        st.success(f"Run completed. Alerts generated: {len(alerts)}")

    st.subheader("Alerts")
    st.dataframe(pd.DataFrame(load_alerts()), use_container_width=True, hide_index=True)
    st.subheader("Rule runs")
    st.dataframe(pd.DataFrame(load_rule_runs()), use_container_width=True, hide_index=True)


def main():
    st.sidebar.title("ATS POC Navigation")
    seed_if_missing()

    if "mock_seed" not in st.session_state:
        st.session_state.mock_seed = 42

    data_source = st.sidebar.radio("Data source", ["Mock", "Real"], index=0)

    if data_source == "Mock":
        if st.sidebar.button("Regenerate mock data"):
            st.session_state.mock_seed += 1
            load_mock_data.clear()
        with st.spinner("Loading mock ATS data..."):
            page_candidates = load_mock_data(st.session_state.mock_seed)
    else:
        real_records = load_candidates()
        real_activities = load_activities()
        page_candidates = _real_to_candidate_model(real_records, real_activities)

    st.sidebar.markdown("### Quick access")
    st.sidebar.markdown("- **Kanban** (go to menu option)")

    page = st.sidebar.radio("Go to", ["Home / Dashboard", "Candidates", "Rules Admin", "Kanban"])

    if page == "Home / Dashboard":
        render_dashboard(page_candidates)
    elif page == "Candidates":
        render_candidates(page_candidates)
    elif page == "Rules Admin":
        render_rules_admin(page_candidates)
    elif page == "Kanban":
        render_kanban()


if __name__ == "__main__":
    main()
