
from pathlib import Path
import pandas as pd


def create_features():
    input_path = Path("data/processed/demand_data.csv")

    df = pd.read_csv(
        input_path,
        parse_dates=["demand_date"]
    )

    df = df.sort_values(
        ["product_id", "retailer_id", "demand_date"]
    ).reset_index(drop=True)

    # Calendar features
    df["day_of_week"] = df["demand_date"].dt.day_of_week
    df["month"] = df["demand_date"].dt.month
    df["day_of_month"] = df["demand_date"].dt.day

    # Historical demand features for each product-retailer pair
    groups = df.groupby(
        ["product_id", "retailer_id"]
    )["quantity_sold"]

    df["lag_1"] = groups.shift(1)
    df["lag_7"] = groups.shift(7)

    # Rolling average of the previous 7 days
    df["rolling_mean_7"] = (
        df.groupby(["product_id", "retailer_id"])["quantity_sold"]
        .transform(
            lambda x: x.shift(1).rolling(window=7).mean()
        )
    )

    # Remove rows without sufficient history
    df = df.dropna().reset_index(drop=True)

    # Preserve the original chronological train/test boundary
    split_date = pd.Timestamp("2026-03-14")

    train_df = df[df["demand_date"] < split_date].copy()
    test_df = df[df["demand_date"] >= split_date].copy()

    output_dir = Path("data/processed")
    train_df.to_csv(output_dir / "train_features.csv", index=False)
    test_df.to_csv(output_dir / "test_features.csv", index=False)

    print("Feature engineering completed!")
    print(f"Training records: {len(train_df)}")
    print(f"Testing records: {len(test_df)}")
    print("Features: product_id, retailer_id, day_of_week,")
    print("month, day_of_month, lag_1, lag_7, rolling_mean_7")


if __name__ == "__main__":
    create_features()
