# Model Training

1. Export labeled applications from SQL view `v_candidate_profile` and `applications`.
2. Save dataset as CSV under `ml-service/data/`.
3. Kick off training:
   ```bash
   cd ml-service
   poetry run python -m app.cli.train --dataset data/interview.csv --target interview
   ```
4. Metrics are tracked in MLflow (`mlruns/`).
5. Register model artifact and update backend setting `ml.active_model`.

Bias report endpoint `/bias_report` expects a CSV with demographic attributes (opt-in) and returns fairness metrics.
