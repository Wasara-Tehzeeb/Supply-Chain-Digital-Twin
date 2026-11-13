
import simpy

from src.ml.predict_demand import predict_demand
from src.ml.predict_supplier_delay import predict_supplier_delay
from src.digital_twin.network import SupplyChainNetwork
from src.digital_twin.auto_replenishment import AutomaticReplenishment
from src.digital_twin.warehouse_replenishment import WarehouseReplenishment


def run_integrated_twin():
    # Step 1: Predict retailer demand
    predicted_demand = predict_demand(
        product_id=1,
        retailer_id=1,
    )

    daily_demand = max(0, round(float(predicted_demand)))

    # Step 2: Predict supplier delay
    supplier_data = {
        "supplier_id": 2,
        "supplier_reliability": 0.88,
        "expected_lead_time": 8,
        "distance_km": 1200,
        "order_quantity": 500,
        "weather_severity": 2,
        "traffic_level": 3,
    }

    delay_prediction = predict_supplier_delay(**supplier_data)

    additional_delay = (
        3 if delay_prediction["predicted_delayed"] else 0
    )

    supplier_lead_time = (
        supplier_data["expected_lead_time"]
        + additional_delay
    )

    # Step 3: Create supply chain network
    env = simpy.Environment()
    network = SupplyChainNetwork(env)

    network.add_node("Supplier", initial_stock=2000)
    network.add_node("Warehouse", initial_stock=300)
    network.add_node("Retailer", initial_stock=100)

    # Step 4: Retailer replenishment
    retailer = AutomaticReplenishment(
        env=env,
        network=network,
        warehouse="Warehouse",
        retailer="Retailer",
        daily_demand=daily_demand,
        reorder_point=40,
        reorder_quantity=150,
        lead_time=3,
    )

    # Step 5: Warehouse replenishment
    warehouse = WarehouseReplenishment(
        env=env,
        network=network,
        supplier="Supplier",
        warehouse="Warehouse",
        reorder_point=200,
        reorder_quantity=500,
        lead_time=supplier_lead_time,
    )

    env.process(retailer.monitor_inventory())
    env.process(warehouse.monitor_warehouse())

    print("\nINTEGRATED ML SUPPLY CHAIN DIGITAL TWIN")
    print("-" * 65)
    print(f"Predicted Daily Demand: {daily_demand}")
    print(
        "Supplier Delay Probability: "
        f"{delay_prediction['delay_probability']:.2%}"
    )
    print(f"Supplier Risk Level: {delay_prediction['risk_level']}")
    print(f"Supplier Lead Time: {supplier_lead_time} days")
    print("-" * 65)

    # Step 6: Run simulation
    env.run(until=30)

    # Step 7: Calculate metrics
    total_demand = retailer.total_demand
    fulfilled = retailer.total_fulfilled
    unfulfilled = total_demand - fulfilled

    fulfillment_rate = (
        fulfilled / total_demand * 100
        if total_demand > 0
        else 0
    )

    print("\nFINAL SIMULATION RESULTS")
    print("-" * 65)
    print(f"Total Demand: {total_demand}")
    print(f"Fulfilled Demand: {fulfilled}")
    print(f"Unfulfilled Demand: {unfulfilled}")
    print(f"Stockout Days: {retailer.stockout_days}")
    print(f"Fulfillment Rate: {fulfillment_rate:.2f}%")

    for name, node in network.nodes.items():
        print(f"{name} Final Stock: {node.stock}")

    print(f"Total Shipments: {len(network.shipments)}")

    print("\nSHIPMENT SUMMARY")
    for shipment in network.shipments:
        print(shipment)


if __name__ == "__main__":
    run_integrated_twin()
