
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.dummy import DummyClassifier
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    roc_auc_score,
    log_loss,
)

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_PATH = (
    BASE_DIR / "data" / "processed" / "supplier_delivery_data.csv"
)

FEATURES = [
    "supplier_id",
    "supplier_reliability",
    "expected_lead_time",
    "distance_km",
    "order_quantity",
    "weather_severity",
    "traffic_level",
]


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

    models = {
        "Majority Baseline": DummyClassifier(
            strategy="most_frequent"
        ),
        "Logistic Regression": make_pipeline(
            StandardScaler(),
            LogisticRegression(
                max_iter=1000,
                random_state=42
            )
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            random_state=42,
            class_weight="balanced",
            n_jobs=-1,
        ),
    }

    print("\nSUPPLIER DELAY MODEL COMPARISON")
    print("-" * 75)

    for name, model in models.items():
        model.fit(X_train, y_train)

        predictions = model.predict(X_test)
        probabilities = model.predict_proba(X_test)[:, 1]

        accuracy = accuracy_score(y_test, predictions)
        f1 = f1_score(y_test, predictions)
        auc = roc_auc_score(y_test, probabilities)
        loss = log_loss(y_test, probabilities)

        print(f"\n{name}")
        print(f"Accuracy: {accuracy:.4f}")
        print(f"F1 Score: {f1:.4f}")
        print(f"ROC-AUC: {auc:.4f}")
        print(f"Log Loss: {loss:.4f}")


if __name__ == "__main__":
    main()
