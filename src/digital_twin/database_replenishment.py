
import simpy

from src.ml.predict_demand import predict_demand
from src.digital_twin.database_network import create_database_network
from src.digital_twin.auto_replenishment import AutomaticReplenishment


def run_database_replenishment():
    env, network, data = create_database_network(product_id=1)

    print("\nDATABASE-DRIVEN REPLENISHMENT SIMULATION")
    print("-" * 65)
    print(f"Product: {data['product']['name']}")

    retailer_processes = []

    for retailer in data["retailers"]:
        retailer_id = retailer["id"]
        retailer_name = f"Retailer_{retailer_id}"

        # Demo routing: match warehouse and retailer IDs.
        warehouse_name = f"Warehouse_{retailer_id}"

        inventory_record = next(
            record
            for record in data["inventory"]
            if record["retailer_id"] == retailer_id
        )

        predicted_demand = predict_demand(
            product_id=data["product"]["id"],
            retailer_id=retailer_id,
        )

        daily_demand = max(
            0,
            round(float(predicted_demand)),
        )

        replenishment = AutomaticReplenishment(
            env=env,
            network=network,
            warehouse=warehouse_name,
            retailer=retailer_name,
            daily_demand=daily_demand,
            reorder_point=inventory_record["reorder_point"],
            reorder_quantity=150,
            lead_time=3,
        )

        env.process(replenishment.monitor_inventory())
        retailer_processes.append(
            (retailer_name, replenishment)
        )

        print(
            f"{retailer_name} | "
            f"Warehouse: {warehouse_name} | "
            f"Predicted Demand: {daily_demand} units/day"
        )

    print("-" * 65)

    env.run(until=20)

    print("\nFINAL SIMULATION RESULTS")
    print("-" * 65)

    total_demand = 0
    total_fulfilled = 0

    for retailer_name, replenishment in retailer_processes:
        demand = replenishment.total_demand
        fulfilled = replenishment.total_fulfilled

        total_demand += demand
        total_fulfilled += fulfilled

        fulfillment_rate = (
            fulfilled / demand * 100
            if demand > 0
            else 0
        )

        print(
            f"{retailer_name} | "
            f"Demand: {demand} | "
            f"Fulfilled: {fulfilled} | "
            f"Stockouts: {replenishment.stockout_days} | "
            f"Fulfillment: {fulfillment_rate:.2f}%"
        )

    print("\nNETWORK INVENTORY")
    for name, node in network.nodes.items():
        print(f"{name}: {node.stock} units")

    print("\nOVERALL PERFORMANCE")
    print(f"Total Demand: {total_demand}")
    print(f"Total Fulfilled: {total_fulfilled}")
    print(f"Unfulfilled Demand: {total_demand - total_fulfilled}")

    overall_rate = (
        total_fulfilled / total_demand * 100
        if total_demand > 0
        else 0
    )

    print(f"Overall Fulfillment Rate: {overall_rate:.2f}%")
    print(f"Total Shipments: {len(network.shipments)}")


if __name__ == "__main__":
    run_database_replenishment()
