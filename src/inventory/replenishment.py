
from math import ceil

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.ml.predict_demand import predict_demand
from src.data.database import engine
from src.data.models import (
    Inventory,
    Product,
    Supplier,
    Retailer,
)


def calculate_reorder_quantity(
    current_stock,
    daily_demand,
    lead_time,
    safety_stock,
):
    target_stock = ceil(
        daily_demand * lead_time + safety_stock
    )

    return max(0, target_stock - current_stock)


def generate_replenishment_recommendations():
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

        print("\nML-BASED INVENTORY REPLENISHMENT RECOMMENDATIONS")
        print("-" * 100)

        for inventory, product, supplier, retailer in records:

            # Predict daily demand using trained Random Forest
            predicted_demand = predict_demand(
                product.product_id,
                retailer.retailer_id
            )

            # Calculate recommended reorder quantity
            reorder_quantity = calculate_reorder_quantity(
                current_stock=inventory.quantity,
                daily_demand=predicted_demand,
                lead_time=supplier.average_lead_time_days,
                safety_stock=inventory.safety_stock,
            )

            # Determine replenishment status
            status = (
                "REORDER REQUIRED"
                if reorder_quantity > 0
                else "SUFFICIENT STOCK"
            )

            print(
                f"Product: {product.product_name} | "
                f"Retailer: {retailer.retailer_name} | "
                f"ML Predicted Demand: {predicted_demand:.2f} | "
                f"Lead Time: {supplier.average_lead_time_days} days | "
                f"Stock: {inventory.quantity} | "
                f"Reorder Qty: {reorder_quantity} | "
                f"Status: {status}"
            )

        print("-" * 100)
        print(f"Total retailer inventory records analyzed: {len(records)}")


if __name__ == "__main__":
    generate_replenishment_recommendations()
