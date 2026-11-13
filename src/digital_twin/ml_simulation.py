
import simpy

from src.ml.predict_demand import predict_demand
from src.digital_twin.network import SupplyChainNetwork
from src.digital_twin.auto_replenishment import AutomaticReplenishment
from src.digital_twin.warehouse_replenishment import WarehouseReplenishment


def run_ml_simulation():
    product_id = 1
    retailer_id = 1

    # Predict next-day demand using the trained ML model
    predicted_demand = predict_demand(
        product_id=product_id,
        retailer_id=retailer_id,
    )

    # Convert forecast to whole inventory units
    daily_demand = max(0, round(float(predicted_demand)))

    print("\nML-POWERED SUPPLY CHAIN DIGITAL TWIN")
    print("-" * 65)
    print(f"Product ID: {product_id}")
    print(f"Retailer ID: {retailer_id}")
    print(f"Predicted Daily Demand: {daily_demand}")

    env = simpy.Environment()
    network = SupplyChainNetwork(env)

    network.add_node("Supplier", initial_stock=2000)
    network.add_node("Warehouse", initial_stock=300)
    network.add_node("Retailer", initial_stock=100)

    retailer_replenishment = AutomaticReplenishment(
        env=env,
        network=network,
        warehouse="Warehouse",
        retailer="Retailer",
        daily_demand=daily_demand,
        reorder_point=40,
        reorder_quantity=150,
        lead_time=3,
    )

    warehouse_replenishment = WarehouseReplenishment(
        env=env,
        network=network,
        supplier="Supplier",
        warehouse="Warehouse",
        reorder_point=200,
        reorder_quantity=500,
        lead_time=4,
    )

    env.process(retailer_replenishment.monitor_inventory())
    env.process(warehouse_replenishment.monitor_warehouse())

    env.run(until=20)

    print("\nML SIMULATION RESULTS")
    print("-" * 65)

    total_demand = retailer_replenishment.total_demand
    total_fulfilled = retailer_replenishment.total_fulfilled

    fulfillment_rate = (
        total_fulfilled / total_demand * 100
        if total_demand > 0
        else 0
    )

    print(f"Total Demand: {total_demand}")
    print(f"Fulfilled Demand: {total_fulfilled}")
    print(f"Stockout Days: {retailer_replenishment.stockout_days}")
    print(f"Fulfillment Rate: {fulfillment_rate:.2f}%")

    for name, node in network.nodes.items():
        print(f"{name} Final Stock: {node.stock}")

    print(f"Total Shipments: {len(network.shipments)}")


if __name__ == "__main__":
    run_ml_simulation()
