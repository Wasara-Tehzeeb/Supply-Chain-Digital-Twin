# ML Pipeline: Versioned, Leak-Free, Reproducible

Covers the four gate requirements: DVC + validation, leakage-free splits + baselines,
MLflow tracking + registry, one-command reproduction. No PostgreSQL needed for this part.

## Layout
| Path | Purpose |
|---|---|
| `params.yaml` | All hyper-parameters, split fractions, seed (tracked by DVC, logged to MLflow) |
| `dvc.yaml` | Stages: `generate_data -> validate -> prepare -> train` |
| `.dvc/config`, `.dvcignore` | DVC config (local remote `dvc_storage/`) |
| `src/pipeline/generate_data.py` | Deterministic raw data to `data/raw/` (`--source postgres` exports the real table) |
| `src/pipeline/validate.py` | Schema + quality gate (nulls, dtypes, ranges, duplicates, missing days, class balance, corrupt/empty files). Exits 1 on failure |
| `src/pipeline/prepare.py` | Past-only features + strict time-ordered train/val/test split + leakage assertions |
| `src/pipeline/train.py` | Baselines first, then RF grid; MLflow runs; model registry |
| `src/pipeline/reproduce.py` | Compares fresh metrics to `reports/expected_metrics.json` |
| `src/pipeline/run_all.py` | **The one command** |
| `Dockerfile` | Same one command in a container |

## Design decisions
* **Demand split**: by date, 70/15/15. Every train date < every validation date < every test date (`assert_no_leakage`).
  Features use only earlier days (`lag_1`, `lag_7`, `shift(1)` rolling mean), and a test proves that changing future values cannot change earlier features.
* **Supplier split**: ordered by `shipment_id` (treated as chronological), same 70/15/15.
* **Model selection** uses validation only; test is scored once on the selected model.
* **Baselines logged first**: rule-based (seasonal-naive lag-7, naive lag-1, 7-day moving average; majority class, low-reliability rule) and classical (Ridge, LogisticRegression).
* **Primary models**: `ResidualForestRegressor` (RF predicting deviation from the trailing 7-day mean, because trees cannot extrapolate a trend) and `RandomForestClassifier`.
* **Registry gate** (`registry_gate` in `params.yaml`): the primary model is registered as `demand_forecaster` / `supplier_delay_classifier` (alias `champion`) only if it beats the best rule-based baseline on validation. Set `all_baselines` to also require beating the classical baseline.
* **Dataset versions** logged to each MLflow run as tags: SHA-256 of raw/train files plus the git commit.

## VS Code setup
```bash
# 1. open the folder in VS Code:  File > Open Folder > Supply-Chain-Digital-Twin
# 2. open a terminal (Ctrl+`) and create the environment (Python 3.11+)
python -m venv .venv
source .venv/bin/activate            # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements-pipeline.txt
# 3. VS Code: Ctrl+Shift+P > "Python: Select Interpreter" > pick .venv
```
(`.vscode/settings.json` already sets `PYTHONPATH` and pytest.)

## Run it
```bash
python -m pytest tests/test_pipeline_validation.py tests/test_pipeline_splits.py -q   # 14 tests
python -m src.pipeline.run_all        # ONE command: whole pipeline + metric verification
```
Docker alternative:
```bash
docker build -t scdt-ml .
docker run --rm scdt-ml
```

## DVC
```bash
git init                      # skip if already a git repo
dvc repro                     # runs generate_data -> validate -> prepare -> train
dvc dag                       # screenshot-able pipeline graph
dvc params diff               # changed params
dvc push                      # stores tracked data in ./dvc_storage (local remote)
git add dvc.yaml dvc.lock params.yaml .dvc .dvcignore data/.gitignore reports/
git commit -m "Add DVC pipeline"
```
`.dvc/` is already in the repo, so do not run `dvc init`. For a cloud remote later:
`dvc remote add -d s3store s3://<bucket>/dvc` (the AWS part of your plan).

## MLflow: runs and registered model (for your screenshots)
```bash
python -m src.pipeline.run_all                 # creates mlflow.db + mlartifacts/
mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000
# open http://127.0.0.1:5000
```
Screenshots to take:
1. **Experiments > supply-chain-digital-twin**: table of runs. Add columns `kind`, `val_rmse`, `test_rmse`, `val_roc_auc`.
   Baseline runs (`baseline_*`) appear before the `rf_*` candidates.
2. Click the run tagged `selected=true`: shows parameters, metrics and `data_version_*` tags.
3. **Models** tab: `demand_forecaster` and `supplier_delay_classifier`, Version 1, alias `champion`.

Exported logs for the submission:
```bash
python -m src.pipeline.export_mlflow_logs
# -> reports/mlflow_runs.csv, reports/mlflow_registered_models.json
# also commit reports/registered_metrics.json and reports/validation_*.json
```

## Demonstrate the validation gate (nice to show the grader)
```bash
python -m src.pipeline.generate_data
# corrupt a value, e.g. blank one quantity_sold cell in data/raw/demand_history.csv
python -m src.pipeline.train    # aborts: "data validation failed; refusing to train"
```

## Honest notes on the results
* Demand: the primary RF beats every rule baseline clearly. The data is almost linear plus noise, so the classical Ridge baseline is on par or slightly better on validation. The pipeline reports this instead of hiding it.
* Supplier delay: the synthetic signal is weak (AUC about 0.55-0.62), so expect modest numbers. Real shipment history would raise it.
* Metrics are reproducible within 0.1% (`reproduce.rel_tolerance`) given the pinned library versions.
