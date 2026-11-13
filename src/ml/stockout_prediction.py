
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.data.database import engine
from src.data.models import (
    Inventory,
    Product,
    Supplier,
    Retailer,
)
from src.ml.predict_demand import predict_demand


def calculate_stockout_risk(
    current_stock,
    predicted_daily_demand,
    lead_time,
):
    expected_demand = predicted_daily_demand * lead_time

    if expected_demand <= 0:
        return "LOW", 0.0

    coverage_ratio = current_stock / expected_demand

    if coverage_ratio < 0.5:
        risk = "HIGH"
    elif coverage_ratio < 1.0:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    return risk, coverage_ratio


def predict_stockout_risks():
    with Session(engine) as session:
        statement = (
            select(Inventory, Product, Supplier, Retailer)
            .join(
                Product,
                Inventory.product_id == Product.product_id
            )
            .join(
                Supplier,
                Product.supplier_id == Supplier.supplier_id
            )
            .join(
                Retailer,
                Inventory.retailer_id == Retailer.retailer_id
            )
            .order_by(Inventory.inventory_id)
        )

        records = session.execute(statement).all()

        print("\nML-BASED STOCKOUT RISK ASSESSMENT")
        print("-" * 100)

        for inventory, product, supplier, retailer in records:

            # Predict daily demand using Random Forest
            predicted_demand = predict_demand(
                product.product_id,
                retailer.retailer_id
            )

            # Calculate stockout risk
            risk, coverage_ratio = calculate_stockout_risk(
                current_stock=inventory.quantity,
                predicted_daily_demand=predicted_demand,
                lead_time=supplier.average_lead_time_days,
            )

            print(
                f"Product: {product.product_name} | "
                f"Retailer: {retailer.retailer_name} | "
                f"Stock: {inventory.quantity} | "
                f"Predicted Daily Demand: {predicted_demand:.2f} | "
                f"Lead Time: {supplier.average_lead_time_days} days | "
                f"Coverage Ratio: {coverage_ratio:.2f} | "
                f"Risk: {risk}"
            )

        print("-" * 100)
        print(f"Total inventory records analyzed: {len(records)}")


if __name__ == "__main__":
    predict_stockout_risks()
