
from pathlib import Path
import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]
OUTPUT_PATH = BASE_DIR / "data" / "processed" / "supplier_delivery_data.csv"


def generate_supplier_data():
    rng = np.random.default_rng(42)

    supplier_configs = {
        1: {"lead_time": 5, "reliability": 0.95},
        2: {"lead_time": 8, "reliability": 0.88},
        3: {"lead_time": 3, "reliability": 0.97},
    }

    records = []

    for shipment_id in range(1, 1001):
        supplier_id = int(rng.choice(list(supplier_configs.keys())))
        supplier = supplier_configs[supplier_id]

        distance_km = int(rng.integers(50, 1501))
        order_quantity = int(rng.integers(20, 501))
        weather_severity = int(rng.integers(0, 4))
        traffic_level = int(rng.integers(0, 4))

        expected_lead_time = supplier["lead_time"]

        delay_score = (
            -2.0
            + (1 - supplier["reliability"]) * 5
            + distance_km / 1500
            + weather_severity * 0.4
            + traffic_level * 0.3
            + order_quantity / 1000
        )

        delay_probability = 1 / (1 + np.exp(-delay_score))

        is_delayed = int(
            rng.random() < delay_probability
        )

        records.append({
            "shipment_id": shipment_id,
            "supplier_id": supplier_id,
            "supplier_reliability": supplier["reliability"],
            "expected_lead_time": expected_lead_time,
            "distance_km": distance_km,
            "order_quantity": order_quantity,
            "weather_severity": weather_severity,
            "traffic_level": traffic_level,
            "is_delayed": is_delayed,
        })

    df = pd.DataFrame(records)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    print("\nSYNTHETIC SUPPLIER DELIVERY DATA")
    print("-" * 55)
    print(f"Total Shipments: {len(df)}")
    print(f"Delayed Shipments: {df['is_delayed'].sum()}")
    print(f"On-Time Shipments: {(df['is_delayed'] == 0).sum()}")
    print(f"Suppliers: {df['supplier_id'].nunique()}")
    print(f"Dataset Saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    generate_supplier_data()
