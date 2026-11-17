"""Automated schema + data-quality gate. Exits non-zero on any failure so
`dvc repro` / the training script stop BEFORE a model is trained.

Checks: file exists & parses, required columns, dtypes, nulls, value ranges,
categorical domains, duplicate keys, date continuity per series, minimum
volume, and class balance (supplier). Writes reports/validation_<name>.json.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

from src.pipeline.config import RAW_DEMAND, RAW_SUPPLIER, REPORTS_DIR


class DataValidationError(Exception):
    pass


def _numeric(df, col):
    return pd.api.types.is_numeric_dtype(df[col])


def validate_demand(df: pd.DataFrame, min_rows: int = 100) -> list[str]:
    errs: list[str] = []
    required = {"demand_date": None, "product_id": "int", "retailer_id": "int",
                "quantity_sold": "int"}
    missing = [c for c in required if c not in df.columns]
    if missing:
        return [f"missing columns: {missing}"]
    if len(df) < min_rows:
        errs.append(f"too few rows: {len(df)} < {min_rows}")
    nulls = df[list(required)].isnull().sum()
    for c, n in nulls.items():
        if n:
            errs.append(f"column '{c}' has {n} null values")
    for c in ("product_id", "retailer_id", "quantity_sold"):
        if not _numeric(df, c):
            errs.append(f"column '{c}' is not numeric (corrupted values?)")
    dates = pd.to_datetime(df["demand_date"], errors="coerce")
    bad_dates = int(dates.isna().sum())
    if bad_dates:
        errs.append(f"{bad_dates} unparseable/missing demand_date values")
    if _numeric(df, "quantity_sold"):
        if (df["quantity_sold"] < 0).any():
            errs.append("quantity_sold contains negative values")
        if df["quantity_sold"].max() > 10_000:
            errs.append("quantity_sold has implausible outliers (>10000)")
    if errs:
        return errs  # structural problems: skip deeper checks
    if df.duplicated(["product_id", "retailer_id", "demand_date"]).any():
        errs.append("duplicate (product_id, retailer_id, demand_date) records")
    tmp = df.assign(_d=dates)
    for (p, r), g in tmp.groupby(["product_id", "retailer_id"]):
        full = pd.date_range(g["_d"].min(), g["_d"].max(), freq="D")
        gaps = len(full) - g["_d"].nunique()
        if gaps:
            errs.append(f"series (product={p}, retailer={r}) has {gaps} missing days")
    return errs


def validate_supplier(df: pd.DataFrame, min_rows: int = 100) -> list[str]:
    errs: list[str] = []
    ranges = {
        "supplier_reliability": (0.0, 1.0), "expected_lead_time": (1, 60),
        "distance_km": (1, 20_000), "order_quantity": (1, 100_000),
        "weather_severity": (0, 3), "traffic_level": (0, 3),
        "is_delayed": (0, 1), "supplier_id": (1, 10_000),
    }
    required = ["shipment_id", *ranges]
    missing = [c for c in required if c not in df.columns]
    if missing:
        return [f"missing columns: {missing}"]
    if len(df) < min_rows:
        errs.append(f"too few rows: {len(df)} < {min_rows}")
    for c in required:
        n = int(df[c].isnull().sum())
        if n:
            errs.append(f"column '{c}' has {n} null values")
        if not _numeric(df, c):
            errs.append(f"column '{c}' is not numeric (corrupted values?)")
    if errs:
        return errs
    for c, (lo, hi) in ranges.items():
        bad = int(((df[c] < lo) | (df[c] > hi)).sum())
        if bad:
            errs.append(f"column '{c}': {bad} values outside [{lo}, {hi}]")
    if df["shipment_id"].duplicated().any():
        errs.append("duplicate shipment_id values")
    rate = df["is_delayed"].mean()
    if not 0.02 <= rate <= 0.98:
        errs.append(f"degenerate class balance: delay rate={rate:.3f}")
    return errs


VALIDATORS = {"demand": (RAW_DEMAND, validate_demand),
              "supplier": (RAW_SUPPLIER, validate_supplier)}


def validate_file(name: str, path: Path | None = None) -> dict:
    default_path, fn = VALIDATORS[name]
    path = Path(path or default_path)
    report = {"dataset": name, "path": str(path), "passed": False, "errors": []}
    if not path.exists():
        report["errors"].append("file not found")
    else:
        try:
            df = pd.read_csv(path)
        except Exception as exc:  # corrupted / unparseable file
            report["errors"].append(f"cannot parse CSV: {exc}")
        else:
            if df.empty:
                report["errors"].append("file is empty")
            else:
                report["rows"] = int(len(df))
                report["errors"].extend(fn(df))
    report["passed"] = not report["errors"]
    return report


def run_validation(names=("demand", "supplier"), raise_on_fail: bool = True) -> list[dict]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    reports = [validate_file(n) for n in names]
    for r in reports:
        (REPORTS_DIR / f"validation_{r['dataset']}.json").write_text(
            json.dumps(r, indent=2))
        status = "PASS" if r["passed"] else "FAIL"
        print(f"[validate] {r['dataset']}: {status}")
        for e in r["errors"]:
            print(f"           - {e}")
    if raise_on_fail and not all(r["passed"] for r in reports):
        raise DataValidationError("data validation failed; refusing to train")
    return reports


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--datasets", nargs="*", default=["demand", "supplier"])
    a = ap.parse_args()
    try:
        run_validation(a.datasets)
    except DataValidationError as e:
        print(f"[validate] ERROR: {e}", file=sys.stderr)
        sys.exit(1)
