
from pathlib import Path
import pandas as pd


def split_demand_data():
    input_path = Path("data/processed/demand_data.csv")

    df = pd.read_csv(
        input_path,
        parse_dates=["demand_date"]
    )

    # Get all unique dates in chronological order.
    unique_dates = sorted(df["demand_date"].unique())

    split_index = int(len(unique_dates) * 0.8)
    split_date = unique_dates[split_index]

    # Train on earlier dates, test on later dates.
    train_df = df[df["demand_date"] < split_date].copy()
    test_df = df[df["demand_date"] >= split_date].copy()

    output_dir = Path("data/processed")
    train_df.to_csv(output_dir / "train_demand.csv", index=False)
    test_df.to_csv(output_dir / "test_demand.csv", index=False)

    print("Demand dataset split successfully!")
    print(f"Training records: {len(train_df)}")
    print(f"Testing records: {len(test_df)}")
    print(f"Training period: {train_df['demand_date'].min().date()} "
          f"to {train_df['demand_date'].max().date()}")
    print(f"Testing period: {test_df['demand_date'].min().date()} "
          f"to {test_df['demand_date'].max().date()}")


if __name__ == "__main__":
    split_demand_data()
