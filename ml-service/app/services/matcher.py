from typing import List, Tuple
import numpy as np


def cosine_match(candidate_vector: List[float], job_vector: List[float]) -> Tuple[float, list[str]]:
    cand = np.array(candidate_vector)
    job = np.array(job_vector)
    if cand.size == 0 or job.size == 0:
        return 0.0, []
    score = float(np.dot(cand, job) / (np.linalg.norm(cand) * np.linalg.norm(job)))
    top_features = ["skill_alignment", "experience_years", "language_fit"]
    return score, top_features
