
from pathlib import Path

import joblib
import pandas as pd

from src.data.database import engine


BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = BASE_DIR / "models" / "demand_forecast_model.pkl"

FEATURES = [
    "product_id",
    "retailer_id",
    "day_of_week",
    "month",
    "day_of_month",
    "lag_1",
    "lag_7",
    "rolling_mean_7",
]


def predict_demand(product_id, retailer_id):
    model = joblib.load(MODEL_PATH)

    query = """
        SELECT demand_date, quantity_sold
        FROM demand_history
        WHERE product_id = %(product_id)s
          AND retailer_id = %(retailer_id)s
        ORDER BY demand_date DESC
        LIMIT 7
    """

    history = pd.read_sql(
        query,
        engine,
        params={
            "product_id": product_id,
            "retailer_id": retailer_id,
        },
    )

    if len(history) < 7:
        raise ValueError(
            "At least 7 days of demand history are required."
        )

    history = history.sort_values("demand_date")

    next_date = pd.to_datetime(
        history["demand_date"].max()
    ) + pd.Timedelta(days=1)

    feature_row = pd.DataFrame([{
        "product_id": product_id,
        "retailer_id": retailer_id,
        "day_of_week": next_date.day_of_week,
        "month": next_date.month,
        "day_of_month": next_date.day,
        "lag_1": history["quantity_sold"].iloc[-1],
        "lag_7": history["quantity_sold"].iloc[0],
        "rolling_mean_7": history["quantity_sold"].mean(),
    }])

    prediction = model.predict(feature_row[FEATURES])[0]

    return max(0, float(prediction))


if __name__ == "__main__":
    print("\nML DEMAND PREDICTION")
    print("-" * 50)

    for product_id in range(1, 4):
        for retailer_id in range(1, 4):
            prediction = predict_demand(
                product_id,
                retailer_id,
            )

            print(
                f"Product {product_id} | "
                f"Retailer {retailer_id} | "
                f"Predicted Daily Demand: {prediction:.2f}"
            )
