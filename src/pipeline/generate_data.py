"""Deterministically generate the raw datasets (no database required).

The demand formula mirrors src/data/seed_data.py so the CSV matches what the
PostgreSQL seeding produces; the supplier generator mirrors
src/ml/generate_supplier_data.py. Raw files land in data/raw/ and are tracked
by DVC (see dvc.yaml).

Optional: `--source postgres` exports the real demand_history table instead.
"""
from __future__ import annotations

import argparse
import random
from datetime import date, timedelta

import numpy as np
import pandas as pd

from src.pipeline.config import RAW_DEMAND, RAW_DIR, RAW_SUPPLIER, load_params

PRODUCT_IDS = [1, 2, 3]
RETAILER_IDS = [1, 2, 3]
SUPPLIERS = {
    1: {"lead_time": 5, "reliability": 0.95},
    2: {"lead_time": 8, "reliability": 0.88},
    3: {"lead_time": 3, "reliability": 0.97},
}


def generate_demand(days: int, start: date) -> pd.DataFrame:
    rows = []
    for product_id in PRODUCT_IDS:
        for retailer_id in RETAILER_IDS:
            for day in range(days):
                d = start + timedelta(days=day)
                rng = random.Random(product_id * 10000 + retailer_id * 100 + day)
                quantity = max(0, round(
                    15 + product_id * 4
                    + (6 if d.weekday() >= 5 else 0)
                    + day * 0.08
                    + rng.gauss(0, 4)
                ))
                rows.append((d.isoformat(), product_id, retailer_id, quantity))
    return pd.DataFrame(
        rows, columns=["demand_date", "product_id", "retailer_id", "quantity_sold"]
    )


def generate_suppliers(n: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    for shipment_id in range(1, n + 1):
        sid = int(rng.choice(list(SUPPLIERS)))
        s = SUPPLIERS[sid]
        distance = int(rng.integers(50, 1501))
        qty = int(rng.integers(20, 501))
        weather = int(rng.integers(0, 4))
        traffic = int(rng.integers(0, 4))
        score = (-2.0 + (1 - s["reliability"]) * 5 + distance / 1500
                 + weather * 0.4 + traffic * 0.3 + qty / 1000)
        delayed = int(rng.random() < 1 / (1 + np.exp(-score)))
        rows.append({
            "shipment_id": shipment_id, "supplier_id": sid,
            "supplier_reliability": s["reliability"],
            "expected_lead_time": s["lead_time"], "distance_km": distance,
            "order_quantity": qty, "weather_severity": weather,
            "traffic_level": traffic, "is_delayed": delayed,
        })
    return pd.DataFrame(rows)


def export_demand_from_postgres() -> pd.DataFrame:
    from sqlalchemy import text
    from src.data.database import engine

    q = text("SELECT demand_date, product_id, retailer_id, quantity_sold "
             "FROM demand_history ORDER BY product_id, retailer_id, demand_date")
    with engine.connect() as conn:
        return pd.read_sql(q, conn)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=["synthetic", "postgres"], default="synthetic")
    args = ap.parse_args()

    p = load_params()
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    if args.source == "postgres":
        demand = export_demand_from_postgres()
    else:
        demand = generate_demand(
            p["data"]["demand_days"], date.fromisoformat(p["data"]["start_date"])
        )
    supplier = generate_suppliers(p["data"]["n_shipments"], p["seed"])

    demand.to_csv(RAW_DEMAND, index=False)
    supplier.to_csv(RAW_SUPPLIER, index=False)
    print(f"[generate] demand rows={len(demand)} -> {RAW_DEMAND}")
    print(f"[generate] supplier rows={len(supplier)} -> {RAW_SUPPLIER}")


if __name__ == "__main__":
    main()
