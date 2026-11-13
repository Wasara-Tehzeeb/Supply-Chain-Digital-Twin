
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

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


def evaluate_model():
    test_df = pd.read_csv("data/processed/test_features.csv")

    model = joblib.load("models/demand_forecast_model.pkl")

    y_true = test_df["quantity_sold"]
    y_pred = model.predict(test_df[FEATURES])

    baseline_pred = test_df["lag_7"]

    for name, predictions in [
        ("Random Forest", y_pred),
        ("7-Day Baseline", baseline_pred),
    ]:
        mae = mean_absolute_error(y_true, predictions)
        rmse = mean_squared_error(y_true, predictions) ** 0.5
        r2 = r2_score(y_true, predictions)

        print(f"\n{name}")
        print(f"MAE: {mae:.4f}")
        print(f"RMSE: {rmse:.4f}")
        print(f"R2 Score: {r2:.4f}")

    # Save evaluation metrics as JSON
    metrics = {
        "model": "RandomForestRegressor",
        "random_forest": {
            "mae": float(mean_absolute_error(y_true, y_pred)),
            "rmse": float(mean_squared_error(y_true, y_pred) ** 0.5),
            "r2": float(r2_score(y_true, y_pred)),
        },
        "seven_day_baseline": {
            "mae": float(mean_absolute_error(y_true, baseline_pred)),
            "rmse": float(mean_squared_error(y_true, baseline_pred) ** 0.5),
            "r2": float(r2_score(y_true, baseline_pred)),
        },
    }

    output_dir = Path("models")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "demand_model_metrics.json"

    with open(output_path, "w") as file:
        json.dump(metrics, file, indent=4)

    print(f"\nEvaluation metrics saved to: {output_path}")


if __name__ == "__main__":
    evaluate_model()
