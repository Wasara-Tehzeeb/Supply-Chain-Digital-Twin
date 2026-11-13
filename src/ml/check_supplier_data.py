
from sqlalchemy import text

from src.data.database import engine


def check_supplier_data():
    query = text("""
        SELECT
            COUNT(*) AS total_shipments,
            COUNT(actual_arrival_date) AS completed_shipments,
            COUNT(*) FILTER (
                WHERE actual_arrival_date > expected_arrival_date
            ) AS delayed_shipments,
            COUNT(*) FILTER (
                WHERE actual_arrival_date <= expected_arrival_date
            ) AS on_time_shipments
        FROM shipments
    """)

    with engine.connect() as connection:
        result = connection.execute(query).mappings().one()

    print("\nSUPPLIER DELIVERY DATA ANALYSIS")
    print("-" * 50)
    print(f"Total Shipments: {result['total_shipments']}")
    print(f"Completed Shipments: {result['completed_shipments']}")
    print(f"Delayed Shipments: {result['delayed_shipments']}")
    print(f"On-Time Shipments: {result['on_time_shipments']}")

    if result["completed_shipments"] < 30:
        print("\nInsufficient historical data for ML training.")
        print("Additional labeled shipment records are required.")
    else:
        print("\nHistorical data available for further analysis.")


if __name__ == "__main__":
    check_supplier_data()
