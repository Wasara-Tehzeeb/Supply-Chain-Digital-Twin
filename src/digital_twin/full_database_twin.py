import simpy

from src.digital_twin.database_ml_delay import get_ml_supplier_lead_time

from src.ml.predict_demand import predict_demand
from src.digital_twin.database_network import create_database_network
from src.digital_twin.auto_replenishment import AutomaticReplenishment
from src.digital_twin.warehouse_replenishment import WarehouseReplenishment


def run_full_database_twin():
    env, network, data = create_database_network(product_id=1)

    supplier = data["supplier"]
    supplier_name = f"Supplier_{supplier['id']}"

    delay_result = get_ml_supplier_lead_time(
        product_id=data["product"]["id"]
    )

    adjusted_lead_time = delay_result["adjusted_lead_time"]

    # Simulation-only supplier stock.
    network.nodes[supplier_name].receive_stock(5000)

    initial_inventory = sum(
        node.stock for node in network.nodes.values()
    )

    retailer_processes = []

    print("\nFULL DATABASE-DRIVEN SUPPLY CHAIN DIGITAL TWIN")
    print("-" * 65)
    print(f"Product: {data['product']['name']}")
    print(f"Supplier: {supplier['name']}")
    print(f"Base Supplier Lead Time: {supplier['lead_time']} days")
    print(f"ML Delay Probability: {delay_result['delay_probability']:.2%}")
    print(f"Supplier Risk Level: {delay_result['risk_level']}")
    print(f"Adjusted Supplier Lead Time: {adjusted_lead_time} days")

    for warehouse in data["warehouses"]:
        warehouse_id = warehouse["id"]
        warehouse_name = f"Warehouse_{warehouse_id}"

        record = next(
            item for item in data["inventory"]
            if item["warehouse_id"] == warehouse_id
        )

        warehouse_replenishment = WarehouseReplenishment(
            env=env,
            network=network,
            supplier=supplier_name,
            warehouse=warehouse_name,
            reorder_point=record["reorder_point"],
            reorder_quantity=500,
            lead_time=adjusted_lead_time,
        )

        env.process(
            warehouse_replenishment.monitor_warehouse()
        )

    for retailer in data["retailers"]:
        retailer_id = retailer["id"]
        retailer_name = f"Retailer_{retailer_id}"
        warehouse_name = f"Warehouse_{retailer_id}"

        record = next(
            item for item in data["inventory"]
            if item["retailer_id"] == retailer_id
        )

        predicted_demand = predict_demand(
            product_id=data["product"]["id"],
            retailer_id=retailer_id,
        )

        daily_demand = max(
            0,
            round(float(predicted_demand)),
        )

        retailer_replenishment = AutomaticReplenishment(
            env=env,
            network=network,
            warehouse=warehouse_name,
            retailer=retailer_name,
            daily_demand=daily_demand,
            reorder_point=record["reorder_point"],
            reorder_quantity=150,
            lead_time=3,
        )

        env.process(
            retailer_replenishment.monitor_inventory()
        )

        retailer_processes.append(
            (retailer_name, retailer_replenishment)
        )

        print(
            f"{retailer_name} | "
            f"Daily Demand: {daily_demand} | "
            f"Warehouse: {warehouse_name}"
        )

    print("-" * 65)

    env.run(until=30)

    total_demand = sum(
        process.total_demand
        for _, process in retailer_processes
    )

    total_fulfilled = sum(
        process.total_fulfilled
        for _, process in retailer_processes
    )

    final_inventory = sum(
        node.stock for node in network.nodes.values()
    )

    in_transit = sum(
        shipment["shipped_quantity"]
        for shipment in network.shipments
        if shipment["status"] == "IN_TRANSIT"
    )

    print("\nFINAL SIMULATION RESULTS")
    print("-" * 65)

    for retailer_name, process in retailer_processes:
        print(
            f"{retailer_name} | "
            f"Demand: {process.total_demand} | "
            f"Fulfilled: {process.total_fulfilled} | "
            f"Stockout Days: {process.stockout_days}"
        )

    print("\nNETWORK INVENTORY")
    for name, node in network.nodes.items():
        print(f"{name}: {node.stock} units")

    print("\nOVERALL PERFORMANCE")
    print(f"Total Demand: {total_demand}")
    print(f"Fulfilled Demand: {total_fulfilled}")
    print(f"Unfulfilled Demand: {total_demand - total_fulfilled}")

    fulfillment_rate = (
        total_fulfilled / total_demand * 100
        if total_demand > 0
        else 0
    )

    print(f"Fulfillment Rate: {fulfillment_rate:.2f}%")
    print(f"Total Shipments: {len(network.shipments)}")

    print("\nINVENTORY CONSERVATION")
    print(f"Initial Inventory: {initial_inventory}")
    print(f"Final Inventory: {final_inventory}")
    print(f"In-Transit Inventory: {in_transit}")
    print(f"Fulfilled Demand: {total_fulfilled}")

    conserved = (
        initial_inventory
        == final_inventory + in_transit + total_fulfilled
    )

    print(f"Inventory Conserved: {conserved}")


if __name__ == "__main__":
    run_full_database_twin()
