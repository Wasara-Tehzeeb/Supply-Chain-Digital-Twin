
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.data.database import engine
from src.data.models import (
    Supplier,
    Warehouse,
    Retailer,
    Product,
    Inventory,
)


def load_supply_chain_data(product_id=1):
    with Session(engine) as session:
        product = session.get(Product, product_id)

        if product is None:
            raise ValueError(
                f"Product {product_id} not found"
            )

        supplier = session.get(
            Supplier,
            product.supplier_id,
        )

        warehouses = session.scalars(
            select(Warehouse).order_by(
                Warehouse.warehouse_id
            )
        ).all()

        retailers = session.scalars(
            select(Retailer).order_by(
                Retailer.retailer_id
            )
        ).all()

        inventory_records = session.scalars(
            select(Inventory).where(
                Inventory.product_id == product_id
            )
        ).all()

        data = {
            "product": {
                "id": product.product_id,
                "name": product.product_name,
            },
            "supplier": {
                "id": supplier.supplier_id,
                "name": supplier.supplier_name,
                "lead_time": supplier.average_lead_time_days,
                "reliability": supplier.reliability_score,
            },
            "warehouses": [
                {
                    "id": warehouse.warehouse_id,
                    "name": warehouse.warehouse_name,
                    "capacity": warehouse.capacity,
                }
                for warehouse in warehouses
            ],
            "retailers": [
                {
                    "id": retailer.retailer_id,
                    "name": retailer.retailer_name,
                }
                for retailer in retailers
            ],
            "inventory": [
                {
                    "product_id": record.product_id,
                    "warehouse_id": record.warehouse_id,
                    "retailer_id": record.retailer_id,
                    "quantity": record.quantity,
                    "reorder_point": record.reorder_point,
                    "safety_stock": record.safety_stock,
                }
                for record in inventory_records
            ],
        }

    return data


if __name__ == "__main__":
    data = load_supply_chain_data(product_id=1)

    print("\nPOSTGRESQL SUPPLY CHAIN DATA")
    print("-" * 60)

    print("Product:", data["product"])
    print("Supplier:", data["supplier"])

    print("\nWarehouses:")
    for warehouse in data["warehouses"]:
        print(warehouse)

    print("\nRetailers:")
    for retailer in data["retailers"]:
        print(retailer)

    print("\nInventory:")
    for record in data["inventory"]:
        print(record)
