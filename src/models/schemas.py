from __future__ import annotations

from datetime import datetime, date
from typing import Any

from pydantic import BaseModel, Field


class PipelineStage(BaseModel):
    name: str
    in_date: datetime
    out_date: datetime | None = None
    duration_days: int | None = None
    notes: str = ""
    actor: str


class Activity(BaseModel):
    timestamp: datetime
    type: str
    summary: str
    actor: str
    stage: str


class Candidate(BaseModel):
    id: int
    name: str
    role: str
    country: str
    email: str
    phone: str
    salary: int
    status: str
    recruiter: str
    skills: list[str]
    created_at: datetime
    hired_at: datetime | None = None
    rejected_at: datetime | None = None
    pipeline: list[PipelineStage] = Field(default_factory=list)
    activities: list[Activity] = Field(default_factory=list)


class Rule(BaseModel):
    id: int | None = None
    name: str
    description: str
    is_active: bool = True
    scope: str
    condition: dict[str, Any]
    action: dict[str, Any]
    severity: str = "medium"
    created_at: datetime | None = None
    updated_at: datetime | None = None


class Alert(BaseModel):
    id: int | None = None
    candidate_id: int
    rule_id: int
    timestamp: datetime
    message: str
    severity: str


class RuleRun(BaseModel):
    id: int | None = None
    run_at: datetime
    rules_evaluated: int
    alerts_generated: int
    triggered_by: str = "streamlit-admin"


class DateRange(BaseModel):
    start: date
    end: date
