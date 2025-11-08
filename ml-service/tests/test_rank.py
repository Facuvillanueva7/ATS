import numpy as np
from app.services.matcher import cosine_match


def test_cosine_match_returns_expected_order():
    cand = np.ones(16)
    job = np.ones(16)
    score, factors = cosine_match(cand.tolist(), job.tolist())
    assert score == 1.0
    assert "skill_alignment" in factors
