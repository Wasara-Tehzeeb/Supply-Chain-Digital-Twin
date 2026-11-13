
from pathlib import Path

import joblib
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = BASE_DIR / "models" / "supplier_delay_model.pkl"

FEATURES = [
    "supplier_id",
    "supplier_reliability",
    "expected_lead_time",
    "distance_km",
    "order_quantity",
    "weather_severity",
    "traffic_level",
]


def predict_supplier_delay(
    supplier_id,
    supplier_reliability,
    expected_lead_time,
    distance_km,
    order_quantity,
    weather_severity,
    traffic_level,
):
    model = joblib.load(MODEL_PATH)

    input_data = pd.DataFrame([{
        "supplier_id": supplier_id,
        "supplier_reliability": supplier_reliability,
        "expected_lead_time": expected_lead_time,
        "distance_km": distance_km,
        "order_quantity": order_quantity,
        "weather_severity": weather_severity,
        "traffic_level": traffic_level,
    }])

    delay_probability = float(
        model.predict_proba(input_data[FEATURES])[0][1]
    )

    if delay_probability >= 0.7:
        risk = "HIGH"
    elif delay_probability >= 0.4:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    return {
        "delay_probability": round(delay_probability, 4),
        "risk_level": risk,
        "predicted_delayed": delay_probability >= 0.5,
    }


if __name__ == "__main__":
    print("\nSUPPLIER DELAY PREDICTION")
    print("-" * 60)

    example_shipments = [
        {
            "supplier_id": 1,
            "supplier_reliability": 0.95,
            "expected_lead_time": 5,
            "distance_km": 300,
            "order_quantity": 100,
            "weather_severity": 0,
            "traffic_level": 1,
        },
        {
            "supplier_id": 2,
            "supplier_reliability": 0.88,
            "expected_lead_time": 8,
            "distance_km": 1200,
            "order_quantity": 400,
            "weather_severity": 3,
            "traffic_level": 3,
        },
        {
            "supplier_id": 3,
            "supplier_reliability": 0.97,
            "expected_lead_time": 3,
            "distance_km": 600,
            "order_quantity": 200,
            "weather_severity": 1,
            "traffic_level": 2,
        },
    ]

    for shipment in example_shipments:
        result = predict_supplier_delay(**shipment)

        print(
            f"Supplier: {shipment['supplier_id']} | "
            f"Distance: {shipment['distance_km']} km | "
            f"Delay Probability: "
            f"{result['delay_probability'] * 100:.2f}% | "
            f"Risk: {result['risk_level']} | "
            f"Predicted Delayed: {result['predicted_delayed']}"
        )

    print("-" * 60)
