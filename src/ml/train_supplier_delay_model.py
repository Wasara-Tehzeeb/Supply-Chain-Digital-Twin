
from pathlib import Path

import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    log_loss,
)

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_PATH = (
    BASE_DIR / "data" / "processed" / "supplier_delivery_data.csv"
)

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


def train_supplier_delay_model():
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

    model = make_pipeline(
        StandardScaler(),
        LogisticRegression(
            max_iter=1000,
            random_state=42,
        ),
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)[:, 1]

    print("\nSUPPLIER DELAY MODEL - LOGISTIC REGRESSION")
    print("-" * 60)

    print(f"Training Samples: {len(X_train)}")
    print(f"Testing Samples: {len(X_test)}")

    print(f"Accuracy: {accuracy_score(y_test, predictions):.4f}")
    print(f"Precision: {precision_score(y_test, predictions):.4f}")
    print(f"Recall: {recall_score(y_test, predictions):.4f}")
    print(f"F1 Score: {f1_score(y_test, predictions):.4f}")
    print(f"ROC-AUC: {roc_auc_score(y_test, probabilities):.4f}")
    print(f"Log Loss: {log_loss(y_test, probabilities):.4f}")

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(model, MODEL_PATH)

    print(f"\nModel saved to: {MODEL_PATH}")


if __name__ == "__main__":
    train_supplier_delay_model()
