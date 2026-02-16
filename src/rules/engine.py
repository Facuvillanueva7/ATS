from __future__ import annotations

from datetime import datetime

from src.models.schemas import Alert, Candidate, Rule



def _candidate_matches(rule: Rule, candidate: Candidate) -> bool:
    condition = rule.condition
    status_ok = condition.get("status") is None or candidate.status == condition.get("status")
    salary_ok = condition.get("salary_gte") is None or candidate.salary >= int(condition["salary_gte"])
    recruiter_ok = condition.get("recruiter") is None or candidate.recruiter == condition.get("recruiter")
    return status_ok and salary_ok and recruiter_ok



def _pipeline_matches(rule: Rule, candidate: Candidate) -> bool:
    condition = rule.condition
    stage_name = condition.get("stage")
    duration_threshold = condition.get("duration_gte")

    for stage in candidate.pipeline:
        if stage_name and stage.name != stage_name:
            continue
        if duration_threshold is not None and (stage.duration_days or 0) < int(duration_threshold):
            continue
        return True
    return False



def _activity_matches(rule: Rule, candidate: Candidate) -> bool:
    condition = rule.condition
    activity_type = condition.get("activity_type")
    contains_text = condition.get("contains")

    for item in candidate.activities:
        if activity_type and item.type != activity_type:
            continue
        if contains_text and contains_text.lower() not in item.summary.lower():
            continue
        return True
    return False



def evaluate_rule(rule: Rule, candidate: Candidate) -> bool:
    if not rule.is_active:
        return False

    if rule.scope == "candidate":
        return _candidate_matches(rule, candidate)
    if rule.scope == "pipeline":
        return _pipeline_matches(rule, candidate)
    if rule.scope == "activity":
        return _activity_matches(rule, candidate)

    return False



def run_rules(candidates: list[Candidate], rules: list[Rule]) -> list[Alert]:
    alerts: list[Alert] = []

    for rule in rules:
        for candidate in candidates:
            if not evaluate_rule(rule, candidate):
                continue
            message = rule.action.get("message", f"Rule '{rule.name}' triggered")
            alerts.append(
                Alert(
                    candidate_id=candidate.id,
                    rule_id=rule.id or -1,
                    timestamp=datetime.now(),
                    message=f"{message} (Candidate: {candidate.name})",
                    severity=rule.severity,
                )
            )

    return alerts
