from __future__ import annotations

import random
from datetime import datetime, timedelta

from faker import Faker

from src.models.schemas import Activity, Candidate, PipelineStage


PIPELINE_STAGES = [
    "Phone/Email",
    "HR",
    "Criteria",
    "Technical",
    "Client",
    "Decision",
    "Offer",
]

INCIDENCE_TYPES = [
    "delay",
    "rejected_salary",
    "missing_references",
    "no_show",
    "client_feedback",
    "background_check",
]

SKILLS_POOL = [
    "SQL",
    "SQLServer",
    ".NET",
    "C#",
    "React",
    "Angular",
    "DevOps",
    "ETL",
    "Power BI",
    "Python",
    "Azure",
    "AWS",
    "Docker",
    "Kubernetes",
]

ROLES = [
    "Data Engineer",
    "BI Analyst",
    "Backend Developer",
    "Full Stack Developer",
    "DevOps Engineer",
    "Data Analyst",
    "QA Automation",
]

RECRUITERS = ["Ana Perez", "Carlos Ruiz", "Marina Soto", "Diego Vega", "Lucia Moreno"]

STATUSES = (["New"] * 10) + (["In Progress"] * 25) + (["Rejected"] * 15) + (["Hired"] * 10)



def _build_pipeline(base_date: datetime, status: str, rng: random.Random, recruiter: str) -> list[PipelineStage]:
    stages: list[PipelineStage] = []
    current = base_date

    max_stage = len(PIPELINE_STAGES)
    if status == "New":
        max_stage = 2
    elif status == "In Progress":
        max_stage = rng.randint(3, 6)
    elif status == "Rejected":
        max_stage = rng.randint(3, 7)

    for idx, stage_name in enumerate(PIPELINE_STAGES[:max_stage]):
        duration = rng.randint(1, 7)
        out_date = current + timedelta(days=duration)
        notes = "Smooth progress"

        if rng.random() < 0.2:
            notes = rng.choice(
                [
                    "Candidate requested schedule change",
                    "Panel feedback delayed",
                    "Need extra validation with manager",
                ]
            )

        if idx == max_stage - 1 and status in {"In Progress", "New"}:
            out_date = None

        stages.append(
            PipelineStage(
                name=stage_name,
                in_date=current,
                out_date=out_date,
                duration_days=(duration if out_date else None),
                notes=notes,
                actor=recruiter,
            )
        )

        if out_date:
            current = out_date + timedelta(days=rng.randint(0, 2))

    return stages



def _build_activities(
    pipeline: list[PipelineStage],
    rng: random.Random,
    recruiter: str,
    include_incidence: bool,
) -> list[Activity]:
    activities: list[Activity] = []
    for stage in pipeline:
        activities.append(
            Activity(
                timestamp=stage.in_date,
                type="progress",
                summary=f"Candidate entered stage: {stage.name}",
                actor=recruiter,
                stage=stage.name,
            )
        )

        if stage.out_date:
            activities.append(
                Activity(
                    timestamp=stage.out_date,
                    type="feedback",
                    summary=f"Completed stage: {stage.name}",
                    actor=rng.choice([recruiter, "Tech Lead", "Hiring Manager"]),
                    stage=stage.name,
                )
            )

        if include_incidence and rng.random() < 0.35:
            incidence_type = rng.choice(INCIDENCE_TYPES)
            incidence_time = stage.in_date + timedelta(hours=rng.randint(4, 36))
            activities.append(
                Activity(
                    timestamp=incidence_time,
                    type=incidence_type,
                    summary=f"Incidence registered: {incidence_type.replace('_', ' ')}",
                    actor=rng.choice([recruiter, "Ops Coordinator", "Client Partner"]),
                    stage=stage.name,
                )
            )

    activities.sort(key=lambda x: x.timestamp)
    return activities



def generate_mock_candidates(seed: int = 42, n: int = 60) -> list[Candidate]:
    fake = Faker("es_ES")
    Faker.seed(seed)
    rng = random.Random(seed)

    if n != 60:
        raise ValueError("Este POC está calibrado para generar exactamente 60 candidatos.")

    status_pool = STATUSES.copy()
    rng.shuffle(status_pool)

    now = datetime.now()
    candidates: list[Candidate] = []

    for idx in range(1, n + 1):
        status = status_pool[idx - 1]
        created_at = now - timedelta(days=rng.randint(5, 90))
        recruiter = rng.choice(RECRUITERS)

        pipeline = _build_pipeline(created_at, status, rng, recruiter)
        include_incidence = idx % 3 == 0
        activities = _build_activities(pipeline, rng, recruiter, include_incidence)

        hired_at = None
        rejected_at = None

        if status == "Hired":
            last_finished = [s.out_date for s in pipeline if s.out_date]
            hired_at = (max(last_finished) + timedelta(days=rng.randint(0, 3))) if last_finished else None
        elif status == "Rejected":
            last_finished = [s.out_date for s in pipeline if s.out_date]
            rejected_at = (max(last_finished) + timedelta(days=1)) if last_finished else None

        candidate = Candidate(
            id=idx,
            name=fake.name(),
            role=rng.choice(ROLES),
            country=rng.choice(["Argentina", "Chile", "Perú", "Colombia", "México", "España"]),
            email=f"candidate{idx}@example.com",
            phone=fake.phone_number(),
            salary=rng.randint(18000, 70000),
            status=status,
            recruiter=recruiter,
            skills=rng.sample(SKILLS_POOL, k=rng.randint(4, 7)),
            created_at=created_at,
            hired_at=hired_at,
            rejected_at=rejected_at,
            pipeline=pipeline,
            activities=activities,
        )
        candidates.append(candidate)

    return candidates
