from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from random import Random

from src.config import DEFAULT_NEW_STAGE, KANBAN_COLUMNS

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"
REAL_CANDIDATES_FILE = DATA_DIR / "real_candidates.json"
REAL_ACTIVITIES_FILE = DATA_DIR / "real_activities.json"
RULES_FILE = DATA_DIR / "rules.json"
ALERTS_FILE = DATA_DIR / "alerts.json"
RULE_RUNS_FILE = DATA_DIR / "rule_runs.json"


def _read_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default


def _write_json(path: Path, payload) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def seed_candidates(n: int = 20, seed: int = 42) -> list[dict]:
    rng = Random(seed)
    now = datetime.now()
    names = [
        "Sofía Martínez", "Lautaro Gómez", "Camila Rojas", "Valentina Ruiz", "Mateo Díaz",
        "Martín López", "Nicolás Acosta", "Agustina Suárez", "Bruno Varela", "Paula Moreno",
        "Lucía Benítez", "Tomás Herrera", "Micaela Ramos", "Ignacio Pérez", "Julieta Núñez",
        "Facundo Silva", "Carla Vera", "Joaquín Torres", "Milagros Castro", "Franco Medina",
    ]
    roles = ["Data Engineer", "Backend .NET", "BI Analyst", "Full Stack", "DevOps Engineer", "QA Automation"]
    recruiters = ["Ana Perez", "Carlos Ruiz", "Marina Soto", "Diego Vega", "Lucia Moreno"]
    english_levels = ["A2", "B1", "B2", "C1", "C2"]
    hard = ["SQL", "SQLServer", ".NET", "C#", "React", "Angular", "DevOps", "ETL", "Power BI", "Azure", "Docker"]
    soft = ["Communication", "Leadership", "Ownership", "Problem solving", "Adaptability", "Teamwork"]

    candidates = []
    for idx in range(1, n + 1):
        name = names[(idx - 1) % len(names)]
        candidates.append({
            "id": idx,
            "name": name,
            "email": f"candidate_{idx}@example.com",
            "role": rng.choice(roles),
            "position": "Software Engineering",
            "recruiter": rng.choice(recruiters),
            "english_level": rng.choice(english_levels),
            "salary_expectation": rng.randint(18000, 75000),
            "hard_skills": rng.sample(hard, k=rng.randint(3, 6)),
            "soft_skills": rng.sample(soft, k=rng.randint(2, 4)),
            "application_date": (now - timedelta(days=rng.randint(1, 80))).date().isoformat(),
            "days_in_process": rng.randint(1, 90),
            "kanban_stage": rng.choice(KANBAN_COLUMNS),
            "updated_at": now.isoformat(),
        })
    _write_json(REAL_CANDIDATES_FILE, candidates)
    return candidates


def seed_if_missing(seed: int = 42) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    current = _read_json(REAL_CANDIDATES_FILE, None)
    if not isinstance(current, list) or not current:
        seed_candidates(seed=seed)
    if not isinstance(_read_json(REAL_ACTIVITIES_FILE, None), list):
        _write_json(REAL_ACTIVITIES_FILE, [])
    for path in [RULES_FILE, ALERTS_FILE, RULE_RUNS_FILE]:
        if not isinstance(_read_json(path, None), list):
            _write_json(path, [])


def load_candidates() -> list[dict]:
    seed_if_missing()
    candidates = _read_json(REAL_CANDIDATES_FILE, [])
    if not isinstance(candidates, list) or not candidates:
        return seed_candidates()
    return candidates


def save_candidates(candidates: list[dict]) -> None:
    _write_json(REAL_CANDIDATES_FILE, candidates)


def load_activities() -> list[dict]:
    seed_if_missing()
    return _read_json(REAL_ACTIVITIES_FILE, [])


def append_activity(activity: dict) -> None:
    activities = load_activities()
    activities.append(activity)
    _write_json(REAL_ACTIVITIES_FILE, activities)


def add_candidate(payload: dict) -> dict:
    candidates = load_candidates()
    max_id = max([int(c["id"]) for c in candidates if str(c.get("id", "")).isdigit()] or [0])
    candidate = {
        "id": payload.get("id") or max_id + 1,
        "name": payload["name"],
        "email": payload["email"],
        "role": payload.get("role", "Sin definir"),
        "position": payload.get("position", payload.get("role", "General")),
        "recruiter": payload.get("recruiter", "Sin asignar"),
        "english_level": payload.get("english_level", "B1"),
        "salary_expectation": int(payload.get("salary_expectation", 0)),
        "hard_skills": payload.get("hard_skills", []),
        "soft_skills": payload.get("soft_skills", []),
        "application_date": payload.get("application_date") or datetime.now().date().isoformat(),
        "days_in_process": int(payload.get("days_in_process", 0)),
        "kanban_stage": payload.get("kanban_stage", DEFAULT_NEW_STAGE),
        "updated_at": datetime.now().isoformat(),
    }
    candidates.append(candidate)
    save_candidates(candidates)
    return candidate


def update_candidate_stage(candidate_id, to_stage: str, actor: str = "system") -> dict | None:
    if to_stage not in KANBAN_COLUMNS:
        raise ValueError(f"Invalid stage: {to_stage}")
    candidates = load_candidates()
    now = datetime.now().isoformat()
    updated = None
    for candidate in candidates:
        if str(candidate["id"]) == str(candidate_id):
            from_stage = candidate.get("kanban_stage", DEFAULT_NEW_STAGE)
            candidate["kanban_stage"] = to_stage
            candidate["updated_at"] = now
            updated = {"candidate": candidate, "from_stage": from_stage, "to_stage": to_stage}
            break
    if updated is None:
        return None
    save_candidates(candidates)
    append_activity({
        "candidate_id": updated["candidate"]["id"],
        "timestamp": now,
        "type": "stage_change",
        "from_stage": updated["from_stage"],
        "to_stage": updated["to_stage"],
        "actor": actor,
        "summary": f"Candidate moved from {updated['from_stage']} to {updated['to_stage']}",
    })
    return updated["candidate"]


def load_rules() -> list[dict]:
    seed_if_missing()
    return _read_json(RULES_FILE, [])


def save_rules(rules: list[dict]) -> None:
    _write_json(RULES_FILE, rules)


def add_rule(rule: dict) -> dict:
    rules = load_rules()
    next_id = max([r.get("id", 0) for r in rules] or [0]) + 1
    now = datetime.now().isoformat()
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
            payload["updated_at"] = datetime.now().isoformat()
            rules[idx] = payload
            break
    save_rules(rules)


def delete_rule(rule_id: int) -> None:
    save_rules([r for r in load_rules() if r.get("id") != rule_id])


def load_alerts() -> list[dict]:
    seed_if_missing()
    return _read_json(ALERTS_FILE, [])


def append_alerts(alerts: list[dict]) -> None:
    current = load_alerts()
    current.extend(alerts)
    _write_json(ALERTS_FILE, current)


def load_rule_runs() -> list[dict]:
    seed_if_missing()
    return _read_json(RULE_RUNS_FILE, [])


def append_rule_run(run_payload: dict) -> None:
    runs = load_rule_runs()
    runs.append(run_payload)
    _write_json(RULE_RUNS_FILE, runs)
