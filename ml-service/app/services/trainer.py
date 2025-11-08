from dataclasses import dataclass
from typing import Dict, Optional
import uuid

import mlflow
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score


@dataclass
class TrainingResult:
    run_id: str
    metrics: Dict[str, float]


class TrainingService:
    def __init__(self) -> None:
        mlflow.set_tracking_uri("file:./mlruns")

    def train_model(self, target: str, job_id: Optional[str], params: Dict) -> TrainingResult:
        X, y = self._synthetic_dataset(target, job_id)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = LogisticRegression(max_iter=200)
        model.fit(X_train, y_train)
        proba = model.predict_proba(X_test)[:, 1]
        auc = float(roc_auc_score(y_test, proba))
        run_id = str(uuid.uuid4())
        with mlflow.start_run(run_name=f"train-{target}", run_id=run_id):
            mlflow.log_metric("auc", auc)
            mlflow.log_param("target", target)
            if job_id:
                mlflow.log_param("job_id", job_id)
        return TrainingResult(run_id=run_id, metrics={"auc": auc})

    def _synthetic_dataset(self, target: str, job_id: Optional[str]):
        rng = np.random.default_rng(abs(hash((target, job_id))) % 1000)
        X = rng.normal(size=(500, 8))
        weights = rng.normal(size=8)
        logits = X @ weights
        y = (1 / (1 + np.exp(-logits)) > 0.5).astype(int)
        return X, y
