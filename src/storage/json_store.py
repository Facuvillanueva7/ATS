from __future__ import annotations

import json
import random
import uuid
from datetime import date, datetime
from pathlib import Path
from typing import Any

from src.config import DEFAULT_NEW_STAGE, KANBAN_COLUMNS

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"
CANDIDATES_FILE = DATA_DIR / "real_candidates.json"
ACTIVITIES_FILE = DATA_DIR / "real_activities.json"
RULES_FILE = DATA_DIR / "rules.json"
ALERTS_FILE = DATA_DIR / "alerts.json"
RULE_RUNS_FILE = DATA_DIR / "rule_runs.json"


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _safe_read_json(path: Path, default: Any):
    try:
        if not path.exists():
            return default
        raw = json.loads(path.read_text(encoding="utf-8"))
        if raw is None:
            return default
        return raw
    except (json.JSONDecodeError, OSError, ValueError, TypeError):
        return default


def _write_json(path: Path, payload: Any) -> None:
    ensure_data_dir()
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def seed_candidates(n: int = 20, seed: int = 42) -> None:
    ensure_data_dir()

    stages = KANBAN_COLUMNS
    recruiters = ["Facu Villanueva", "Lucia Moreno", "Diego Vega", "Marina Soto", "Ana Perez"]
    roles = ["Fullstack Developer", "Backend Developer", ".NET Dev", "QA Automation", "BA", "DevOps Engineer"]
    english = ["Pre-intermediate", "Intermediate", "Upper-intermediate", "Advanced"]
    hard_pool = ["C#", ".NET", "SQL", "SQLServer", "React", "Angular", "Azure", "AWS", "ETL", "Power BI", "Docker", "Kubernetes"]
    soft_pool = ["Proactivity", "Adaptability", "Empathy", "Active listening", "Ownership", "Communication"]

    rng = random.Random(seed)
    today = date.today()
    items: list[dict[str, Any]] = []

    for idx in range(n):
        app_days = rng.randint(1, 200)
        items.append(
            {
                "id": str(uuid.uuid4())[:8],
                "name": f"Candidate {idx + 1}",
                "email": f"candidate{idx + 1}@example.com",
                "role": rng.choice(roles),
                "position": "Software Engineering",
                "recruiter": rng.choice(recruiters),
                "english_level": rng.choice(english),
                "salary_expectation": rng.randint(1200, 6000),
                "hard_skills": rng.sample(hard_pool, k=rng.randint(3, 6)),
                "soft_skills": rng.sample(soft_pool, k=rng.randint(2, 5)),
                "application_date": str(today),
                "days_in_process": app_days,
                "kanban_stage": rng.choice(stages),
                "updated_at": datetime.utcnow().isoformat(),
            }
        )

    _write_json(CANDIDATES_FILE, items)

    activities = _safe_read_json(ACTIVITIES_FILE, [])
    if not isinstance(activities, list):
        activities = []
    _write_json(ACTIVITIES_FILE, activities)


def seed_if_missing(seed: int = 42) -> None:
    ensure_data_dir()

    candidates = _safe_read_json(CANDIDATES_FILE, None)
    if not isinstance(candidates, list) or len(candidates) == 0:
        seed_candidates(20, seed)

    activities = _safe_read_json(ACTIVITIES_FILE, None)
    if not isinstance(activities, list):
        _write_json(ACTIVITIES_FILE, [])

    if not isinstance(_safe_read_json(RULES_FILE, None), list):
        _write_json(
            RULES_FILE,
            [
                {
                    "id": 1,
                    "name": "High salary rejected",
                    "description": "Alert when rejected and salary >= 50k",
                    "is_active": True,
                    "scope": "candidate",
                    "condition": {"status": "Rejected", "salary_gte": 50000},
                    "action": {"message": "Rejected candidate with high expected salary"},
                    "severity": "high",
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                }
            ],
        )

    for path in [ALERTS_FILE, RULE_RUNS_FILE]:
        if not isinstance(_safe_read_json(path, None), list):
            _write_json(path, [])


def load_candidates() -> list[dict]:
    ensure_data_dir()
    if not CANDIDATES_FILE.exists():
        seed_candidates(20)

    raw = _safe_read_json(CANDIDATES_FILE, None)
    if not isinstance(raw, list) or len(raw) == 0:
        seed_candidates(20)
        raw = _safe_read_json(CANDIDATES_FILE, [])
    return raw if isinstance(raw, list) else []


def save_candidates(items: list[dict]) -> None:
    _write_json(CANDIDATES_FILE, items)


def load_activities() -> list[dict]:
    ensure_data_dir()
    data = _safe_read_json(ACTIVITIES_FILE, [])
    if not isinstance(data, list):
        _write_json(ACTIVITIES_FILE, [])
        return []
    return data


def append_activity(activity: dict) -> None:
    activities = load_activities()
    activities.append(activity)
    _write_json(ACTIVITIES_FILE, activities)


def add_candidate(payload: dict) -> dict:
    candidates = load_candidates()

    candidate = {
        "id": payload.get("id") or str(uuid.uuid4())[:8],
        "name": payload["name"],
        "email": payload["email"],
        "role": payload.get("role", "Unknown"),
        "position": payload.get("position", "General"),
        "recruiter": payload.get("recruiter", "Unassigned"),
        "english_level": payload.get("english_level", "Intermediate"),
        "salary_expectation": int(payload.get("salary_expectation", 0)),
        "hard_skills": payload.get("hard_skills", []),
        "soft_skills": payload.get("soft_skills", []),
        "application_date": payload.get("application_date") or str(date.today()),
        "days_in_process": int(payload.get("days_in_process", 0)),
        "kanban_stage": payload.get("kanban_stage", DEFAULT_NEW_STAGE),
        "updated_at": datetime.utcnow().isoformat(),
    }
    candidates.append(candidate)
    save_candidates(candidates)
    return candidate


def update_candidate_stage(candidate_id: str, to_stage: str, actor: str = "system") -> dict | None:
    candidates = load_candidates()
    now = datetime.utcnow().isoformat()
    updated = None

    for candidate in candidates:
        if str(candidate.get("id")) == str(candidate_id):
            from_stage = candidate.get("kanban_stage", DEFAULT_NEW_STAGE)
            candidate["kanban_stage"] = to_stage
            candidate["updated_at"] = now
            updated = {"candidate": candidate, "from_stage": from_stage, "to_stage": to_stage}
            break

    if updated is None:
        return None

    save_candidates(candidates)
    append_activity(
        {
            "candidate_id": updated["candidate"]["id"],
            "timestamp": now,
            "type": "stage_change",
            "from_stage": updated["from_stage"],
            "to_stage": updated["to_stage"],
            "actor": actor,
            "summary": f"Candidate moved from {updated['from_stage']} to {updated['to_stage']}",
        }
    )
    return updated["candidate"]


# Rules/alerts JSON persistence (sin SQLite)
def load_rules() -> list[dict]:
    data = _safe_read_json(RULES_FILE, [])
    return data if isinstance(data, list) else []


def save_rules(rules: list[dict]) -> None:
    _write_json(RULES_FILE, rules)


def add_rule(rule: dict) -> dict:
    rules = load_rules()
    next_id = max([r.get("id", 0) for r in rules] or [0]) + 1
    now = datetime.utcnow().isoformat()
    rule["id"] = next_id
    rule["created_at"] = now
    rule["updated_at"] = now
    rules.append(rule)
    save_rules(rules)
    return rule


def update_rule(rule_id: int, payload: dict) -> None:
    rules = load_rules()
    for idx, rule in enumerate(rules):
        if rule.get("id") == rule_id:
            payload["id"] = rule_id
            payload["created_at"] = rule.get("created_at")
            payload["updated_at"] = datetime.utcnow().isoformat()
            rules[idx] = payload
            break
    save_rules(rules)


def delete_rule(rule_id: int) -> None:
    save_rules([r for r in load_rules() if r.get("id") != rule_id])


def load_alerts() -> list[dict]:
    data = _safe_read_json(ALERTS_FILE, [])
    return data if isinstance(data, list) else []


def append_alerts(alerts: list[dict]) -> None:
    current = load_alerts()
    current.extend(alerts)
    _write_json(ALERTS_FILE, current)


def load_rule_runs() -> list[dict]:
    data = _safe_read_json(RULE_RUNS_FILE, [])
    return data if isinstance(data, list) else []


def append_rule_run(run_payload: dict) -> None:
    runs = load_rule_runs()
    runs.append(run_payload)
    _write_json(RULE_RUNS_FILE, runs)
