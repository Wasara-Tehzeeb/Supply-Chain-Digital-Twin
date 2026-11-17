"""Export MLflow runs + registered models to reports/ (for submission evidence).

    python -m src.pipeline.export_mlflow_logs
Creates: reports/mlflow_runs.csv, reports/mlflow_registered_models.json
"""
from __future__ import annotations

import json

import mlflow
from mlflow.tracking import MlflowClient

from src.pipeline.config import REPORTS_DIR, load_params


def main() -> None:
    p = load_params()
    mlflow.set_tracking_uri(p["mlflow"]["tracking_uri"])
    client = MlflowClient()
    exp = client.get_experiment_by_name(p["mlflow"]["experiment"])
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    runs = mlflow.search_runs(experiment_ids=[exp.experiment_id])
    runs.to_csv(REPORTS_DIR / "mlflow_runs.csv", index=False)
    print(f"[export] {len(runs)} runs -> reports/mlflow_runs.csv")

    models = []
    for rm in client.search_registered_models():
        versions = client.search_model_versions(f"name='{rm.name}'")
        models.append({
            "name": rm.name, "aliases": dict(rm.aliases),
            "versions": [{"version": v.version, "run_id": v.run_id, "tags": dict(v.tags),
                          "source": v.source} for v in versions],
        })
    (REPORTS_DIR / "mlflow_registered_models.json").write_text(json.dumps(models, indent=2))
    print(f"[export] {len(models)} registered models -> reports/mlflow_registered_models.json")


if __name__ == "__main__":
    main()
