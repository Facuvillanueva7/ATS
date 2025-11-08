from dataclasses import dataclass
from typing import Dict

import numpy as np


@dataclass
class PredictionResult:
    yhat: float
    shap: Dict[str, float]


class PredictorService:
    def __init__(self) -> None:
        self._models = {
            "interview": self._baseline_model,
            "offer": self._baseline_model,
            "success3m": self._baseline_model,
        }

    def predict(self, model: str, features: Dict[str, float]) -> PredictionResult:
        if model not in self._models:
            raise KeyError(f"model {model} not registered")
        return self._models[model](features)

    def _baseline_model(self, features: Dict[str, float]) -> PredictionResult:
        values = np.array(list(features.values()) or [0])
        score = float(1 / (1 + np.exp(-values.mean())))
        shap = {key: float(val - values.mean()) for key, val in features.items()}
        return PredictionResult(yhat=score, shap=shap)
