
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.data.database import engine
from src.data.models import Inventory, Product, Warehouse, Retailer


def monitor_inventory():
    with Session(engine) as session:
        statement = (
            select(Inventory, Product, Warehouse, Retailer)
            .join(Product, Inventory.product_id == Product.product_id)
            .outerjoin(
                Warehouse,
                Inventory.warehouse_id == Warehouse.warehouse_id
            )
            .outerjoin(
                Retailer,
                Inventory.retailer_id == Retailer.retailer_id
            )
            .order_by(Inventory.inventory_id)
        )

        records = session.execute(statement).all()

        print("\nSUPPLY CHAIN INVENTORY MONITOR")
        print("-" * 85)

        for inventory, product, warehouse, retailer in records:
            location = (
                warehouse.warehouse_name
                if warehouse is not None
                else retailer.retailer_name
            )

            status = get_stock_status(
                inventory.quantity,
                inventory.reorder_point,
                inventory.safety_stock
            )

            print(
                f"Product: {product.product_name} | "
                f"Location: {location} | "
                f"Quantity: {inventory.quantity} | "
                f"Reorder Point: {inventory.reorder_point} | "
                f"Safety Stock: {inventory.safety_stock} | "
                f"Status: {status}"
            )

        print("-" * 85)
        print(f"Total inventory records monitored: {len(records)}")

def get_stock_status(quantity, reorder_point, safety_stock):
    if quantity <= safety_stock:
        return "CRITICAL"
    elif quantity <= reorder_point:
        return "LOW STOCK"
    return "HEALTHY"


if __name__ == "__main__":
    monitor_inventory()
