
from pathlib import Path

import pandas as pd
from sqlalchemy import text

from src.data.database import engine


def prepare_demand_data():
    query = text("""
        SELECT
            demand_date,
            product_id,
            retailer_id,
            quantity_sold
        FROM demand_history
        ORDER BY product_id, retailer_id, demand_date
    """)

    with engine.connect() as connection:
        df = pd.read_sql(query, connection)

    df["demand_date"] = pd.to_datetime(df["demand_date"])

    # Validate the dataset.
    if df.empty:
        raise ValueError("No demand history found")

    if df.isnull().any().any():
        raise ValueError("Dataset contains missing values")

    duplicates = df.duplicated(
        subset=["product_id", "retailer_id", "demand_date"]
    ).sum()

    if duplicates:
        raise ValueError(f"Found {duplicates} duplicate records")

    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "demand_data.csv"
    df.to_csv(output_path, index=False)

    print("Demand dataset prepared successfully!")
    print(f"Total records: {len(df)}")
    print(f"Unique products: {df['product_id'].nunique()}")
    print(f"Unique retailers: {df['retailer_id'].nunique()}")
    print(
        f"Date range: {df['demand_date'].min().date()} "
        f"to {df['demand_date'].max().date()}"
    )
    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    prepare_demand_data()
