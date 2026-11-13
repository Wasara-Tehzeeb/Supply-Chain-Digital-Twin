
from pathlib import Path
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.dummy import DummyClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
)

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_PATH = BASE_DIR / "data" / "processed" / "supplier_delivery_data.csv"
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


def evaluate_model(name, y_true, predictions):
    print(f"\n{name}")
    print("-" * 40)
    print(f"Accuracy: {accuracy_score(y_true, predictions):.4f}")
    print(f"Precision: {precision_score(y_true, predictions, zero_division=0):.4f}")
    print(f"Recall: {recall_score(y_true, predictions, zero_division=0):.4f}")
    print(f"F1 Score: {f1_score(y_true, predictions, zero_division=0):.4f}")


def main():
    df = pd.read_csv(DATA_PATH)

    X = df[FEATURES]
    y = df["is_delayed"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    model = joblib.load(MODEL_PATH)
    model_predictions = model.predict(X_test)

    baseline = DummyClassifier(strategy="most_frequent")
    baseline.fit(X_train, y_train)
    baseline_predictions = baseline.predict(X_test)

    print("\nSUPPLIER DELAY MODEL EVALUATION")

    evaluate_model(
        "Random Forest",
        y_test,
        model_predictions,
    )

    evaluate_model(
        "Majority-Class Baseline",
        y_test,
        baseline_predictions,
    )


if __name__ == "__main__":
    main()
