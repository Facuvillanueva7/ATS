from __future__ import annotations

from collections import Counter, defaultdict
from datetime import timedelta

import pandas as pd
import plotly.express as px

from src.models.schemas import Candidate



def funnel_chart(candidates: list[Candidate]):
    counter = Counter()
    for candidate in candidates:
        for stage in candidate.pipeline:
            counter[stage.name] += 1
    df = pd.DataFrame({"stage": list(counter.keys()), "count": list(counter.values())})
    return px.funnel(df, x="count", y="stage", title="Pipeline funnel by stage")



def avg_days_per_stage_chart(candidates: list[Candidate]):
    data = defaultdict(list)
    for candidate in candidates:
        for stage in candidate.pipeline:
            if stage.duration_days is not None:
                data[stage.name].append(stage.duration_days)
    result = {stage: sum(values) / len(values) for stage, values in data.items() if values}
    df = pd.DataFrame({"stage": list(result.keys()), "avg_days": list(result.values())})
    df = df.sort_values("avg_days", ascending=False)
    return px.bar(df, x="stage", y="avg_days", title="Average days per stage")



def incidences_by_type_chart(candidates: list[Candidate]):
    counter = Counter()
    for candidate in candidates:
        for activity in candidate.activities:
            if activity.type not in {"progress", "feedback"}:
                counter[activity.type] += 1
    df = pd.DataFrame({"type": list(counter.keys()), "count": list(counter.values())})
    return px.bar(df, x="type", y="count", title="Incidences by type")



def weekly_trend_chart(candidates: list[Candidate]):
    if not candidates:
        return px.line(title="Weekly trend")

    start = min(c.created_at for c in candidates).date()
    end = max(c.created_at for c in candidates).date() + timedelta(days=21)
    all_days = pd.date_range(start=start, end=end, freq="D")
    df = pd.DataFrame({"date": all_days})
    df["created"] = 0
    df["hired"] = 0
    df["rejected"] = 0

    for candidate in candidates:
        df.loc[df["date"] == pd.Timestamp(candidate.created_at.date()), "created"] += 1
        if candidate.hired_at:
            df.loc[df["date"] == pd.Timestamp(candidate.hired_at.date()), "hired"] += 1
        if candidate.rejected_at:
            df.loc[df["date"] == pd.Timestamp(candidate.rejected_at.date()), "rejected"] += 1

    weekly = df.resample("W", on="date").sum().reset_index()
    long_df = weekly.melt(id_vars="date", value_vars=["created", "hired", "rejected"], var_name="metric", value_name="value")
    return px.line(long_df, x="date", y="value", color="metric", markers=True, title="Weekly trend")
