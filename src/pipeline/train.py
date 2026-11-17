"""Baselines -> primary model -> MLflow tracking -> model registry.

Order of operations per task (demand / supplier):
  1. Log BASELINE runs (rule-based + classical) on validation and test.
  2. Grid-search the primary RandomForest on VALIDATION; every candidate is
     an MLflow run with hyper-parameters, dataset hashes and metrics.
  3. Pick the best candidate by validation metric; report test metrics once.
  4. Register it in the MLflow Model Registry (versioned, alias 'champion')
     only if it beats the best baseline on validation.
Writes reports/registered_metrics.json (used by `reproduce` to verify).
"""
from __future__ import annotations

import itertools
import json

import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from mlflow.tracking import MlflowClient
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import (
    accuracy_score, f1_score, mean_absolute_error, mean_squared_error,
    r2_score, roc_auc_score,
)
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from src.pipeline.config import (
    DEMAND_FEATURES, DEMAND_TARGET, PROCESSED_DIR, RAW_DEMAND, RAW_SUPPLIER,
    REPORTS_DIR, SUPPLIER_FEATURES, SUPPLIER_TARGET, file_sha256, git_commit,
    load_params,
)
from src.pipeline.models import ResidualForestRegressor
from src.pipeline.validate import run_validation


# ---------------------------------------------------------------- metrics
def reg_metrics(y, pred) -> dict:
    return {"mae": float(mean_absolute_error(y, pred)),
            "rmse": float(mean_squared_error(y, pred) ** 0.5),
            "r2": float(r2_score(y, pred))}


def clf_metrics(y, pred, score) -> dict:
    return {"accuracy": float(accuracy_score(y, pred)),
            "f1": float(f1_score(y, pred, zero_division=0)),
            # constant scores (e.g. majority-class baseline) -> AUC is 0.5 by definition
            "roc_auc": 0.5 if np.ptp(score) == 0 else float(roc_auc_score(y, score))}


# ---------------------------------------------------------------- helpers
def _load(prefix: str):
    return tuple(pd.read_csv(PROCESSED_DIR / f"{prefix}_{s}.csv") for s in ("train", "val", "test"))


def _log_run(run_name, task, kind, params, data_tags, val_m, test_m=None,
             model=None, extra_tags=None):
    """One MLflow run: params, dataset versions, metrics, optional model."""
    with mlflow.start_run(run_name=run_name) as run:
        mlflow.set_tags({"task": task, "kind": kind, "git_commit": git_commit(),
                         **data_tags, **(extra_tags or {})})
        mlflow.log_params({k: ("None" if v is None else v) for k, v in params.items()})
        mlflow.log_metrics({f"val_{k}": v for k, v in val_m.items()})
        if test_m:
            mlflow.log_metrics({f"test_{k}": v for k, v in test_m.items()})
        if model is not None:
            mlflow.sklearn.log_model(
                model,
                artifact_path="model",
                skops_trusted_types=[
                    "sklearn.tree._tree.Tree",
                    "src.pipeline.models.ResidualForestRegressor"
                ]
            )
        return run.info.run_id


def _register(client, run_id, name, alias, metrics_tags) -> str:
    mv = mlflow.register_model(f"runs:/{run_id}/model", name)
    client.set_registered_model_alias(name, alias, mv.version)
    for k, v in metrics_tags.items():
        client.set_model_version_tag(name, mv.version, k, str(v))
    return str(mv.version)


# ---------------------------------------------------------------- demand
def run_demand(p, data_tags, client) -> dict:
    tr, va, te = _load("demand")
    Xtr, ytr = tr[DEMAND_FEATURES], tr[DEMAND_TARGET]
    Xva, yva = va[DEMAND_FEATURES], va[DEMAND_TARGET]
    Xte, yte = te[DEMAND_FEATURES], te[DEMAND_TARGET]
    task = "demand_forecast"
    seed = p["seed"]

    # 1) baselines (logged BEFORE the primary model)
    baselines = {
        "baseline_seasonal_naive_lag7": lambda X: X["lag_7"].values,
        "baseline_naive_lag1": lambda X: X["lag_1"].values,
        "baseline_moving_average_7": lambda X: X["rolling_mean_7"].values,
    }
    best_rule = {"rmse": np.inf}
    for name, fn in baselines.items():
        vm, tm = reg_metrics(yva, fn(Xva)), reg_metrics(yte, fn(Xte))
        _log_run(name, task, "baseline_rule", {"model": name}, data_tags, vm, tm)
        best_rule = min(best_rule, vm, key=lambda m: m["rmse"])
    ridge = make_pipeline(StandardScaler(), Ridge(alpha=1.0)).fit(Xtr, ytr)
    vm, tm = reg_metrics(yva, ridge.predict(Xva)), reg_metrics(yte, ridge.predict(Xte))
    _log_run("baseline_ridge_regression", task, "baseline_classical",
             {"model": "Ridge", "alpha": 1.0}, data_tags, vm, tm, model=ridge)
    classical = vm
    best_base_val = min(best_rule, classical, key=lambda m: m["rmse"])

    # 2) primary model grid on validation
    g = p["demand"]["primary_grid"]
    best = None
    for n, d, leaf in itertools.product(g["n_estimators"], g["max_depth"], g["min_samples_leaf"]):
        hp = {"model": "ResidualForestRegressor", "anchor": "rolling_mean_7",
              "n_estimators": n, "max_depth": d, "min_samples_leaf": leaf,
              "random_state": seed}
        m = ResidualForestRegressor("rolling_mean_7", n, d, leaf, seed).fit(Xtr, ytr)
        vm = reg_metrics(yva, m.predict(Xva))
        run_id = _log_run(f"rf_n{n}_d{d}_l{leaf}", task, "candidate", hp, data_tags, vm, model=m)
        if best is None or vm["rmse"] < best["val"]["rmse"]:
            best = {"run_id": run_id, "val": vm, "model": m, "params": hp}

    # 3) test metrics for the selected model, logged once on its run
    test_m = reg_metrics(yte, best["model"].predict(Xte))
    with mlflow.start_run(run_id=best["run_id"]):
        mlflow.log_metrics({f"test_{k}": v for k, v in test_m.items()})
        mlflow.set_tag("selected", "true")

    # 4) registry gate
    gate = best_rule if p["registry_gate"] == "rule_baselines" else best_base_val
    beats = best["val"]["rmse"] < gate["rmse"]
    version = None
    if beats:
        version = _register(client, best["run_id"], p["mlflow"]["demand_model_name"],
                            p["mlflow"]["alias"],
                            {"val_rmse": best["val"]["rmse"], "test_rmse": test_m["rmse"],
                             "baseline_val_rmse": gate["rmse"]})
    return {"task": task, "registered_version": version, "run_id": best["run_id"],
            "params": best["params"], "val": best["val"], "test": test_m,
            "best_rule_baseline_val": best_rule, "classical_baseline_val": classical,
            "beats_rule_baseline": bool(best["val"]["rmse"] < best_rule["rmse"]),
            "beats_classical_baseline": bool(best["val"]["rmse"] < classical["rmse"]),
            "registry_gate": p["registry_gate"], "registered": bool(beats)}


# -------------------------------------------------------------- supplier
def run_supplier(p, data_tags, client) -> dict:
    tr, va, te = _load("supplier")
    Xtr, ytr = tr[SUPPLIER_FEATURES], tr[SUPPLIER_TARGET]
    Xva, yva = va[SUPPLIER_FEATURES], va[SUPPLIER_TARGET]
    Xte, yte = te[SUPPLIER_FEATURES], te[SUPPLIER_TARGET]
    task, seed = "supplier_delay", p["seed"]
    thr = p["supplier"]["rule_reliability_threshold"]

    def rule(X):
        score = 1.0 - X["supplier_reliability"].values
        return (X["supplier_reliability"].values < thr).astype(int), score

    majority = int(ytr.mean() >= 0.5)
    baselines = {"baseline_majority_class": lambda X: (np.full(len(X), majority),
                                                       np.full(len(X), ytr.mean())),
                 "baseline_rule_low_reliability": rule}
    best_rule = {"roc_auc": -np.inf}
    for name, fn in baselines.items():
        vp, vs = fn(Xva)
        tp, ts = fn(Xte)
        vm, tm = clf_metrics(yva, vp, vs), clf_metrics(yte, tp, ts)
        _log_run(name, task, "baseline_rule", {"model": name, "threshold": thr},
                 data_tags, vm, tm)
        best_rule = max(best_rule, vm, key=lambda m: m["roc_auc"])
    lr = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, random_state=seed)).fit(Xtr, ytr)
    vm = clf_metrics(yva, lr.predict(Xva), lr.predict_proba(Xva)[:, 1])
    tm = clf_metrics(yte, lr.predict(Xte), lr.predict_proba(Xte)[:, 1])
    _log_run("baseline_logistic_regression", task, "baseline_classical",
             {"model": "LogisticRegression"}, data_tags, vm, tm, model=lr)
    classical = vm
    best_base_val = max(best_rule, classical, key=lambda m: m["roc_auc"])

    g = p["supplier"]["primary_grid"]
    best = None
    for n, d, leaf in itertools.product(g["n_estimators"], g["max_depth"], g["min_samples_leaf"]):
        hp = {"model": "RandomForestClassifier", "n_estimators": n, "max_depth": d,
              "min_samples_leaf": leaf, "random_state": seed}
        m = RandomForestClassifier(n_estimators=n, max_depth=d, min_samples_leaf=leaf,
                                   random_state=seed, n_jobs=1).fit(Xtr, ytr)
        vm = clf_metrics(yva, m.predict(Xva), m.predict_proba(Xva)[:, 1])
        run_id = _log_run(f"rf_n{n}_d{d}_l{leaf}", task, "candidate", hp, data_tags, vm, model=m)
        if best is None or vm["roc_auc"] > best["val"]["roc_auc"]:
            best = {"run_id": run_id, "val": vm, "model": m, "params": hp}

    test_m = clf_metrics(yte, best["model"].predict(Xte), best["model"].predict_proba(Xte)[:, 1])
    with mlflow.start_run(run_id=best["run_id"]):
        mlflow.log_metrics({f"test_{k}": v for k, v in test_m.items()})
        mlflow.set_tag("selected", "true")

    gate = best_rule if p["registry_gate"] == "rule_baselines" else best_base_val
    beats = best["val"]["roc_auc"] > gate["roc_auc"]
    version = None
    if beats:
        version = _register(client, best["run_id"], p["mlflow"]["supplier_model_name"],
                            p["mlflow"]["alias"],
                            {"val_roc_auc": best["val"]["roc_auc"],
                             "test_roc_auc": test_m["roc_auc"],
                             "baseline_val_roc_auc": gate["roc_auc"]})
    return {"task": task, "registered_version": version, "run_id": best["run_id"],
            "params": best["params"], "val": best["val"], "test": test_m,
            "best_rule_baseline_val": best_rule, "classical_baseline_val": classical,
            "beats_rule_baseline": bool(best["val"]["roc_auc"] > best_rule["roc_auc"]),
            "beats_classical_baseline": bool(best["val"]["roc_auc"] > classical["roc_auc"]),
            "registry_gate": p["registry_gate"], "registered": bool(beats)}


# ------------------------------------------------------------------ main
def main() -> None:
    p = load_params()
    run_validation()  # fail fast on corrupted / missing inputs
    for f in ("demand_train", "supplier_train"):
        if not (PROCESSED_DIR / f"{f}.csv").exists():
            raise FileNotFoundError(f"{f}.csv missing - run `python -m src.pipeline.prepare` first")

    p.setdefault("registry_gate", "rule_baselines")
    mlflow.set_tracking_uri(p["mlflow"]["tracking_uri"])
    mlflow.set_experiment(p["mlflow"]["experiment"])
    client = MlflowClient()

    data_tags = {
        "data_version_demand_raw": file_sha256(RAW_DEMAND),
        "data_version_supplier_raw": file_sha256(RAW_SUPPLIER),
        "data_version_demand_train": file_sha256(PROCESSED_DIR / "demand_train.csv"),
        "data_version_supplier_train": file_sha256(PROCESSED_DIR / "supplier_train.csv"),
        "params_seed": str(p["seed"]),
    }
    results = {"demand": run_demand(p, data_tags, client),
               "supplier": run_supplier(p, data_tags, client),
               "data_versions": data_tags}
    failed = [k for k in ("demand", "supplier") if not results[k]["registered"]]
    if failed:
        raise SystemExit(f"Registry gate failed for {failed}: primary model did not "
                         f"beat the baseline; nothing registered for them.")

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    out = REPORTS_DIR / "registered_metrics.json"
    out.write_text(json.dumps(results, indent=2))
    for k in ("demand", "supplier"):
        r = results[k]
        print(f"[train] {k}: registered_version={r['registered_version']} "
              f"val={r['val']} test={r['test']}")
        print(f"        rule baseline (val)={r['best_rule_baseline_val']}")
        print(f"        classical baseline (val)={r['classical_baseline_val']}")
        if not r["beats_classical_baseline"]:
            print(f"        NOTE: classical baseline beats the primary model on validation ({k})")
    print(f"[train] wrote {out}")


if __name__ == "__main__":
    main()
