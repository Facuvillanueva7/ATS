"""Stubs para integración futura con APIs reales ATS."""

from __future__ import annotations

from typing import Any



def fetch_candidates_from_api() -> list[dict[str, Any]]:
    """Placeholder: reemplazar por llamada real al endpoint de candidatos."""
    raise NotImplementedError("Implementar integración real de candidatos.")



def fetch_pipeline_events_from_api() -> list[dict[str, Any]]:
    """Placeholder: reemplazar por llamada real al endpoint de pipeline."""
    raise NotImplementedError("Implementar integración real de pipeline.")



def push_rule_to_api(rule_payload: dict[str, Any]) -> None:
    """Placeholder: enviar regla creada en UI a backend real."""
    raise NotImplementedError("Implementar integración real de reglas.")
