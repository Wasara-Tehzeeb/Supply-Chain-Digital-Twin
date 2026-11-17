.PHONY: install test reproduce dvc-repro mlflow-ui export clean
PY ?= python

install:
	$(PY) -m pip install -r requirements-pipeline.txt

test:
	$(PY) -m pytest tests/test_pipeline_validation.py tests/test_pipeline_splits.py -q

# ONE command: reproduces the registered metrics
reproduce:
	$(PY) -m src.pipeline.run_all

dvc-repro:
	dvc repro

mlflow-ui:
	mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000

export:
	$(PY) -m src.pipeline.export_mlflow_logs

clean:
	rm -rf data/raw data/processed mlflow.db mlartifacts mlruns reports/validation_*.json reports/registered_metrics.json
