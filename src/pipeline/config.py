"""Shared paths, params loading and helpers for the ML pipeline."""
from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
PARAMS_PATH = ROOT / "params.yaml"

RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
REPORTS_DIR = ROOT / "reports"
MODELS_DIR = ROOT / "models"

RAW_DEMAND = RAW_DIR / "demand_history.csv"
RAW_SUPPLIER = RAW_DIR / "supplier_deliveries.csv"

DEMAND_TARGET = "quantity_sold"
DEMAND_FEATURES = [
    "product_id", "retailer_id", "day_of_week", "month", "day_of_month",
    "lag_1", "lag_7", "rolling_mean_7",
]

SUPPLIER_TARGET = "is_delayed"
SUPPLIER_FEATURES = [
    "supplier_id", "supplier_reliability", "expected_lead_time",
    "distance_km", "order_quantity", "weather_severity", "traffic_level",
]


def load_params(path: Path = PARAMS_PATH) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def file_sha256(path: Path, n: int = 16) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:n]


def git_commit() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
            capture_output=True, text=True, check=True,
        )
        return out.stdout.strip() or "unknown"
    except Exception:
        return "unknown"
