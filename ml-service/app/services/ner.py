from typing import Dict


_FAKE_SKILLS = {"python", "c#", "azure", "sql", "mlops"}


def ner_extract(text: str) -> Dict[str, object]:
    tokens = text.lower().split()
    skills = sorted({token.strip(",.") for token in tokens if token in _FAKE_SKILLS})
    return {
        "skills": skills,
        "summary": text[:160],
        "confidence": 0.6 + 0.1 * len(skills)
    }
