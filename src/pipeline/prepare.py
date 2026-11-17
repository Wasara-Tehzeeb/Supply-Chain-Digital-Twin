"""Feature engineering + strict time-ordered train/val/test splits.

Leakage controls
  * Features for row t use only information from days < t
    (lags and a shift(1)-ed rolling mean), per product-retailer series.
  * Splits are by DATE (demand) / shipment order (supplier): every train
    timestamp < every validation timestamp < every test timestamp.
  * Hyper-parameters are chosen on validation; test is scored once.
  * assert_no_leakage() runs on every split and raises on any violation.
"""
from __future__ import annotations

import pandas as pd

from src.pipeline.config import (
    DEMAND_TARGET, PROCESSED_DIR, RAW_DEMAND, RAW_SUPPLIER, load_params,
)
from src.pipeline.validate import run_validation


def build_demand_features(df: pd.DataFrame, lags=(1, 7), window: int = 7) -> pd.DataFrame:
    df = df.copy()
    df["demand_date"] = pd.to_datetime(df["demand_date"])
    df = df.sort_values(["product_id", "retailer_id", "demand_date"]).reset_index(drop=True)
    df["day_of_week"] = df["demand_date"].dt.dayofweek
    df["month"] = df["demand_date"].dt.month
    df["day_of_month"] = df["demand_date"].dt.day
    g = df.groupby(["product_id", "retailer_id"])[DEMAND_TARGET]
    for k in lags:
        df[f"lag_{k}"] = g.shift(k)
    df[f"rolling_mean_{window}"] = g.transform(lambda s: s.shift(1).rolling(window).mean())
    return df.dropna().reset_index(drop=True)


def time_split_by_key(df: pd.DataFrame, key: str, train_frac: float, val_frac: float):
    """Split on sorted unique values of `key` so no key value straddles two splits."""
    keys = sorted(df[key].unique())
    n = len(keys)
    i_val = int(n * train_frac)
    i_test = int(n * (train_frac + val_frac))
    if not (0 < i_val < i_test < n):
        raise ValueError("split fractions leave an empty partition")
    t_val, t_test = keys[i_val], keys[i_test]
    train = df[df[key] < t_val].copy()
    val = df[(df[key] >= t_val) & (df[key] < t_test)].copy()
    test = df[df[key] >= t_test].copy()
    return train, val, test


def assert_no_leakage(train, val, test, key: str) -> None:
    assert len(train) and len(val) and len(test), "empty split"
    assert train[key].max() < val[key].min(), f"train/val overlap on '{key}'"
    assert val[key].max() < test[key].min(), f"val/test overlap on '{key}'"


def main() -> None:
    p = load_params()
    run_validation()  # never prepare/train on unvalidated data
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    s = p["split"]

    demand = build_demand_features(
        pd.read_csv(RAW_DEMAND), p["features"]["lags"], p["features"]["rolling_window"])
    tr, va, te = time_split_by_key(demand, "demand_date", s["train_frac"], s["val_frac"])
    assert_no_leakage(tr, va, te, "demand_date")
    for name, d in (("train", tr), ("val", va), ("test", te)):
        d.to_csv(PROCESSED_DIR / f"demand_{name}.csv", index=False)
        print(f"[prepare] demand {name}: {len(d)} rows "
              f"{d['demand_date'].min().date()} -> {d['demand_date'].max().date()}")

    sup = pd.read_csv(RAW_SUPPLIER).sort_values("shipment_id").reset_index(drop=True)
    tr, va, te = time_split_by_key(sup, "shipment_id", s["train_frac"], s["val_frac"])
    assert_no_leakage(tr, va, te, "shipment_id")
    for name, d in (("train", tr), ("val", va), ("test", te)):
        d.to_csv(PROCESSED_DIR / f"supplier_{name}.csv", index=False)
        print(f"[prepare] supplier {name}: {len(d)} rows "
              f"shipment {d['shipment_id'].min()} -> {d['shipment_id'].max()}")


if __name__ == "__main__":
    main()
