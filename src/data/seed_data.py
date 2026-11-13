
from datetime import date, timedelta
from sqlalchemy import select

import json
from pathlib import Path

from src.data.database import engine
from src.data.models import (
    Base, Supplier, Warehouse, Retailer, Product,
    Inventory, Order, Shipment, DemandHistory
)
from sqlalchemy.orm import Session
import random


def get_or_create(session, model, lookup, defaults=None):
    obj = session.scalar(
        select(model).filter_by(**lookup)
    )
    if obj is None:
        obj = model(**lookup, **(defaults or {}))
        session.add(obj)
        session.flush()
    return obj


def seed_database():
    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        suppliers = [
            ("Alpha Manufacturing", "Lahore", 5, 0.95),
            ("Beta Industries", "Karachi", 8, 0.88),
            ("Gamma Supplies", "Islamabad", 3, 0.97),
        ]

        supplier_objects = []
        for name, location, lead_time, reliability in suppliers:
            supplier_objects.append(get_or_create(
                session, Supplier,
                {"supplier_name": name},
                {
                    "location": location,
                    "average_lead_time_days": lead_time,
                    "reliability_score": reliability,
                }
            ))

        warehouses = [
            ("Lahore Central Warehouse", "Lahore", 10000),
            ("Karachi Distribution Center", "Karachi", 15000),
            ("Islamabad Regional Warehouse", "Islamabad", 8000),
        ]

        warehouse_objects = []
        for name, location, capacity in warehouses:
            warehouse_objects.append(get_or_create(
                session, Warehouse,
                {"warehouse_name": name},
                {"location": location, "capacity": capacity}
            ))

        retailers = [
            ("Lahore Retail Store", "Lahore"),
            ("Karachi Retail Store", "Karachi"),
            ("Islamabad Retail Store", "Islamabad"),
        ]

        retailer_objects = []
        for name, location in retailers:
            retailer_objects.append(get_or_create(
                session, Retailer,
                {"retailer_name": name},
                {"location": location}
            ))

        products = [
            ("Laptop", "Electronics", 150000.0, 0),
            ("Smartphone", "Electronics", 65000.0, 1),
            ("Headphones", "Accessories", 5000.0, 2),
        ]

        product_objects = []
        for name, category, price, supplier_index in products:
            product_objects.append(get_or_create(
                session, Product,
                {"product_name": name},
                {
                    "category": category,
                    "unit_price": price,
                    "supplier_id": supplier_objects[supplier_index].supplier_id,
                }
            ))

        for product in product_objects:
            for warehouse in warehouse_objects:
                get_or_create(
                    session, Inventory,
                    {
                        "product_id": product.product_id,
                        "warehouse_id": warehouse.warehouse_id,
                    },
                    {
                        "quantity": 500,
                        "reorder_point": 150,
                        "safety_stock": 75,
                    }
                )

            for retailer in retailer_objects:
                get_or_create(
                    session, Inventory,
                    {
                        "product_id": product.product_id,
                        "retailer_id": retailer.retailer_id,
                    },
                    {
                        "quantity": 100,
                        "reorder_point": 40,
                        "safety_stock": 20,
                    }
                )

        # Fixed dates make sample data reproducible.
        start_date = date(2026, 1, 1)

        for product in product_objects:
            for retailer in retailer_objects:
                for day in range(90):
                    current_date = start_date + timedelta(days=day)
                    rng = random.Random(
                        product.product_id * 10000
                        + retailer.retailer_id * 100
                        + day
                    )

                    base_demand = 15 + product.product_id * 4
                    weekend_effect = 6 if current_date.weekday() >= 5 else 0
                    trend = day * 0.08
                    random_variation = rng.gauss(0, 4)

                    quantity = max(
                        0,
                        round(
                            base_demand
                            + weekend_effect
                            + trend
                            + random_variation
                        )
                    )

                    demand_record = get_or_create(
                        session, DemandHistory,
                        {
                            "product_id": product.product_id,
                            "retailer_id": retailer.retailer_id,
                            "demand_date": current_date,
                        },
                        {"quantity_sold": quantity}
                    )

                    demand_record.quantity_sold = quantity

        for index, product in enumerate(product_objects):
            order_date = date(2026, 4, 1) + timedelta(days=index)

            order = get_or_create(
                session, Order,
                {
                    "product_id": product.product_id,
                    "source_type": "supplier",
                    "source_id": product.supplier_id,
                    "destination_type": "warehouse",
                    "destination_id": warehouse_objects[index].warehouse_id,
                    "order_date": order_date,
                },
                {
                    "quantity": 200,
                    "expected_delivery_date": order_date + timedelta(days=7),
                    "status": "delivered",
                }
            )

            get_or_create(
                session, Shipment,
                {"order_id": order.order_id},
                {
                    "shipped_date": order_date,
                    "expected_arrival_date": order_date + timedelta(days=7),
                    "actual_arrival_date": order_date + timedelta(days=8),
                    "status": "delivered",
                }
            )

        session.commit()

    print("Database seeded successfully!")


if __name__ == "__main__":
    seed_database()
