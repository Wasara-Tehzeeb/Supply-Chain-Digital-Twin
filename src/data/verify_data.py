
from sqlalchemy import text
from src.data.database import engine

tables = [
    "suppliers",
    "warehouses",
    "retailers",
    "products",
    "inventory",
    "orders",
    "shipments",
    "demand_history",
]

with engine.connect() as connection:
    for table in tables:
        count = connection.execute(
            text(f"SELECT COUNT(*) FROM {table}")
        ).scalar()
        print(f"{table}: {count} records")
