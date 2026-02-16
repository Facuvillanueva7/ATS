from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

from src.models.schemas import Alert, Rule


DB_PATH = Path("ats_dashboard.db")



def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn



def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                is_active INTEGER NOT NULL DEFAULT 1,
                scope TEXT NOT NULL,
                condition_json TEXT NOT NULL,
                action_json TEXT NOT NULL,
                severity TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id INTEGER NOT NULL,
                rule_id INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                message TEXT NOT NULL,
                severity TEXT NOT NULL,
                FOREIGN KEY(rule_id) REFERENCES rules(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS rule_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_at TEXT NOT NULL,
                rules_evaluated INTEGER NOT NULL,
                alerts_generated INTEGER NOT NULL,
                triggered_by TEXT NOT NULL
            )
            """
        )



def seed_default_rules() -> None:
    if list_rules():
        return

    defaults = [
        {
            "name": "High salary rejected",
            "description": "Alert when a high salary candidate gets rejected.",
            "scope": "candidate",
            "condition": {"status": "Rejected", "salary_gte": 50000},
            "action": {"message": "Rejected candidate with high expected salary"},
            "severity": "high",
        },
        {
            "name": "Long technical stage",
            "description": "Technical stage over threshold",
            "scope": "pipeline",
            "condition": {"stage": "Technical", "duration_gte": 6},
            "action": {"message": "Technical stage duration exceeds SLA"},
            "severity": "medium",
        },
    ]

    for rule in defaults:
        create_rule(
            Rule(
                name=rule["name"],
                description=rule["description"],
                is_active=True,
                scope=rule["scope"],
                condition=rule["condition"],
                action=rule["action"],
                severity=rule["severity"],
            )
        )



def create_rule(rule: Rule) -> int:
    now = datetime.now().isoformat()
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO rules (name, description, is_active, scope, condition_json, action_json, severity, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                rule.name,
                rule.description,
                int(rule.is_active),
                rule.scope,
                json.dumps(rule.condition),
                json.dumps(rule.action),
                rule.severity,
                now,
                now,
            ),
        )
        return int(cur.lastrowid)



def update_rule(rule_id: int, payload: Rule) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE rules
            SET name=?, description=?, is_active=?, scope=?, condition_json=?, action_json=?, severity=?, updated_at=?
            WHERE id=?
            """,
            (
                payload.name,
                payload.description,
                int(payload.is_active),
                payload.scope,
                json.dumps(payload.condition),
                json.dumps(payload.action),
                payload.severity,
                datetime.now().isoformat(),
                rule_id,
            ),
        )



def delete_rule(rule_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM rules WHERE id=?", (rule_id,))



def list_rules() -> list[Rule]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM rules ORDER BY id DESC").fetchall()

    return [
        Rule(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            is_active=bool(row["is_active"]),
            scope=row["scope"],
            condition=json.loads(row["condition_json"]),
            action=json.loads(row["action_json"]),
            severity=row["severity"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
        for row in rows
    ]



def create_alert(alert: Alert) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO alerts (candidate_id, rule_id, timestamp, message, severity)
            VALUES (?, ?, ?, ?, ?)
            """,
            (alert.candidate_id, alert.rule_id, alert.timestamp.isoformat(), alert.message, alert.severity),
        )
        return int(cur.lastrowid)



def list_alerts(limit: int = 300) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT a.id, a.candidate_id, a.rule_id, a.timestamp, a.message, a.severity, r.name AS rule_name
            FROM alerts a
            LEFT JOIN rules r ON r.id = a.rule_id
            ORDER BY a.timestamp DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]



def create_rule_run(rules_evaluated: int, alerts_generated: int, triggered_by: str = "streamlit-admin") -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO rule_runs (run_at, rules_evaluated, alerts_generated, triggered_by)
            VALUES (?, ?, ?, ?)
            """,
            (datetime.now().isoformat(), rules_evaluated, alerts_generated, triggered_by),
        )
        return int(cur.lastrowid)



def list_rule_runs(limit: int = 50) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM rule_runs ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return [dict(row) for row in rows]
