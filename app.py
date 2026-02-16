from __future__ import annotations

import json
from datetime import date

import pandas as pd
import streamlit as st

from src.charts.charts import (
    avg_days_per_stage_chart,
    funnel_chart,
    incidences_by_type_chart,
    weekly_trend_chart,
)
from src.db.sqlite import (
    create_alert,
    create_rule,
    create_rule_run,
    delete_rule,
    init_db,
    list_alerts,
    list_rule_runs,
    list_rules,
    seed_default_rules,
    update_rule,
)
from src.mock.generator import generate_mock_candidates
from src.models.schemas import Rule
from src.rules.engine import run_rules

st.set_page_config(page_title="ATS Dashboard POC", layout="wide")


@st.cache_data(show_spinner=False)
def load_mock_data(seed: int):
    return generate_mock_candidates(seed=seed, n=60)



def candidates_to_table(candidates):
    records = []
    for c in candidates:
        records.append(
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
        )
    return pd.DataFrame(records)



def activities_df(candidate):
    return pd.DataFrame(
        [
            {
                "timestamp": a.timestamp,
                "type": a.type,
                "summary": a.summary,
                "actor": a.actor,
                "stage": a.stage,
            }
            for a in candidate.activities
        ]
    )



def pipeline_df(candidate):
    return pd.DataFrame(
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



def render_dashboard(candidates):
    st.header("Home / Dashboard")

    statuses = pd.Series([c.status for c in candidates]).value_counts()
    total = len(candidates)
    hired = int(statuses.get("Hired", 0))
    rejected = int(statuses.get("Rejected", 0))
    in_progress = int(statuses.get("In Progress", 0))
    new = int(statuses.get("New", 0))

    tth_values = [
        (c.hired_at - c.created_at).days
        for c in candidates
        if c.hired_at is not None and c.created_at is not None and c.hired_at >= c.created_at
    ]
    avg_tth = sum(tth_values) / len(tth_values) if tth_values else 0

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Total candidates", total)
    col2.metric("New", new)
    col3.metric("In progress", in_progress)
    col4.metric("Rejected", rejected)
    col5.metric("Hired", hired)
    col6.metric("Avg time-to-hire", f"{avg_tth:.1f} days")

    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        st.plotly_chart(funnel_chart(candidates), use_container_width=True)
    with row1_col2:
        st.plotly_chart(avg_days_per_stage_chart(candidates), use_container_width=True)

    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        st.plotly_chart(incidences_by_type_chart(candidates), use_container_width=True)
    with row2_col2:
        st.plotly_chart(weekly_trend_chart(candidates), use_container_width=True)



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
            min_value=int(table["salary"].min()),
            max_value=int(table["salary"].max()),
            value=(int(table["salary"].min()), int(table["salary"].max())),
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

    st.subheader("Candidate detail")
    st.markdown(
        f"""
**{candidate.name}** — {candidate.role}  
📍 {candidate.country} | ✉️ {candidate.email} | 📞 {candidate.phone}  
💰 Salary: {candidate.salary} | 👤 Recruiter: {candidate.recruiter}  
🏷️ Skills: {", ".join(candidate.skills)}
"""
    )

    tab1, tab2 = st.tabs(["Pipeline Timeline", "Logs / Incidences"])

    with tab1:
        p_df = pipeline_df(candidate)
        st.dataframe(p_df, use_container_width=True, hide_index=True)
        st.download_button(
            "Export pipeline CSV",
            data=p_df.to_csv(index=False).encode("utf-8"),
            file_name=f"candidate_{candidate.id}_pipeline.csv",
            mime="text/csv",
        )

    with tab2:
        a_df = activities_df(candidate)
        types = sorted(a_df["type"].unique()) if not a_df.empty else []
        selected_types = st.multiselect("Type", options=types)
        date_bounds = (
            a_df["timestamp"].min().date() if not a_df.empty else date.today(),
            a_df["timestamp"].max().date() if not a_df.empty else date.today(),
        )
        selected_range = st.date_input("Date range", value=date_bounds)

        logs = a_df.copy()
        if selected_types:
            logs = logs[logs["type"].isin(selected_types)]
        if isinstance(selected_range, tuple) and len(selected_range) == 2:
            start, end = selected_range
            logs = logs[(logs["timestamp"].dt.date >= start) & (logs["timestamp"].dt.date <= end)]

        st.dataframe(logs, use_container_width=True, hide_index=True)
        st.download_button(
            "Export activities CSV",
            data=logs.to_csv(index=False).encode("utf-8"),
            file_name=f"candidate_{candidate.id}_activities.csv",
            mime="text/csv",
        )



def render_rules_admin(candidates):
    st.header("Rules Admin")

    rules = list_rules()

    with st.expander("Create rule", expanded=False):
        with st.form("create_rule_form"):
            name = st.text_input("Name")
            description = st.text_area("Description")
            is_active = st.checkbox("Active", value=True)
            scope = st.selectbox("Scope", ["candidate", "pipeline", "activity"])
            condition_str = st.text_area(
                "Condition JSON",
                value='{"status": "Rejected", "salary_gte": 50000}',
                help="Valid JSON",
            )
            action_str = st.text_area(
                "Action JSON",
                value='{"message": "Business rule triggered"}',
                help="Valid JSON",
            )
            severity = st.selectbox("Severity", ["low", "medium", "high", "critical"])
            submitted = st.form_submit_button("Create")

            if submitted:
                try:
                    condition = json.loads(condition_str)
                    action = json.loads(action_str)
                    create_rule(
                        Rule(
                            name=name,
                            description=description,
                            is_active=is_active,
                            scope=scope,
                            condition=condition,
                            action=action,
                            severity=severity,
                        )
                    )
                    st.success("Rule created")
                    st.rerun()
                except json.JSONDecodeError:
                    st.error("Condition/Action JSON inválido")

    st.subheader("Existing rules")
    if not rules:
        st.info("No rules available")
    for rule in rules:
        with st.container(border=True):
            st.markdown(f"**#{rule.id} - {rule.name}** ({rule.scope})")
            st.caption(f"Severity: {rule.severity} | Active: {rule.is_active}")
            st.write(rule.description)
            st.code(json.dumps(rule.condition, indent=2), language="json")
            st.code(json.dumps(rule.action, indent=2), language="json")

            c1, c2 = st.columns(2)
            with c1:
                if st.button(f"Toggle active #{rule.id}"):
                    rule.is_active = not rule.is_active
                    update_rule(rule.id, rule)
                    st.rerun()
            with c2:
                if st.button(f"Delete #{rule.id}"):
                    delete_rule(rule.id)
                    st.rerun()

            with st.expander(f"Edit rule #{rule.id}"):
                with st.form(f"edit_rule_{rule.id}"):
                    new_name = st.text_input("Name", value=rule.name, key=f"name_{rule.id}")
                    new_description = st.text_area("Description", value=rule.description, key=f"desc_{rule.id}")
                    new_scope = st.selectbox(
                        "Scope",
                        ["candidate", "pipeline", "activity"],
                        index=["candidate", "pipeline", "activity"].index(rule.scope),
                        key=f"scope_{rule.id}",
                    )
                    new_condition = st.text_area(
                        "Condition JSON",
                        value=json.dumps(rule.condition),
                        key=f"cond_{rule.id}",
                    )
                    new_action = st.text_area(
                        "Action JSON",
                        value=json.dumps(rule.action),
                        key=f"action_{rule.id}",
                    )
                    new_severity = st.selectbox(
                        "Severity",
                        ["low", "medium", "high", "critical"],
                        index=["low", "medium", "high", "critical"].index(rule.severity),
                        key=f"severity_{rule.id}",
                    )
                    save = st.form_submit_button("Save")
                    if save:
                        try:
                            update_rule(
                                rule.id,
                                Rule(
                                    name=new_name,
                                    description=new_description,
                                    is_active=rule.is_active,
                                    scope=new_scope,
                                    condition=json.loads(new_condition),
                                    action=json.loads(new_action),
                                    severity=new_severity,
                                ),
                            )
                            st.success("Rule updated")
                            st.rerun()
                        except json.JSONDecodeError:
                            st.error("JSON inválido")

    st.subheader("Run rules")
    if st.button("Run rules engine", type="primary"):
        active_rules = [r for r in list_rules() if r.is_active]
        generated_alerts = run_rules(candidates, active_rules)
        for alert in generated_alerts:
            create_alert(alert)
        create_rule_run(rules_evaluated=len(active_rules), alerts_generated=len(generated_alerts))
        st.success(f"Run completed. Alerts generated: {len(generated_alerts)}")

    st.subheader("Alerts")
    alerts = list_alerts()
    if alerts:
        st.dataframe(pd.DataFrame(alerts), use_container_width=True, hide_index=True)
    else:
        st.info("No alerts generated yet.")

    st.subheader("Rule runs audit")
    runs = list_rule_runs()
    if runs:
        st.dataframe(pd.DataFrame(runs), use_container_width=True, hide_index=True)
    else:
        st.info("No runs yet.")



def main():
    st.sidebar.title("ATS POC Navigation")

    init_db()
    seed_default_rules()

    if "mock_seed" not in st.session_state:
        st.session_state.mock_seed = 42

    with st.sidebar:
        st.write("Mock data controls")
        if st.button("Regenerate mock data"):
            st.session_state.mock_seed += 1
            load_mock_data.clear()
            st.success(f"New seed: {st.session_state.mock_seed}")

    try:
        with st.spinner("Loading mock ATS data..."):
            candidates = load_mock_data(st.session_state.mock_seed)
    except Exception as exc:  # noqa: BLE001
        st.error(f"Error loading data: {exc}")
        return

    page = st.sidebar.radio("Go to", ["Home / Dashboard", "Candidates", "Rules Admin"])

    if page == "Home / Dashboard":
        render_dashboard(candidates)
    elif page == "Candidates":
        render_candidates(candidates)
    elif page == "Rules Admin":
        render_rules_admin(candidates)


if __name__ == "__main__":
    main()
