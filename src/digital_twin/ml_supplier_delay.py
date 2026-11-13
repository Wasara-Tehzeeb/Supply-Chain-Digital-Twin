
import simpy

from src.ml.predict_supplier_delay import predict_supplier_delay
from src.digital_twin.network import SupplyChainNetwork


def run_supplier_delay_simulation():
    env = simpy.Environment()
    network = SupplyChainNetwork(env)

    network.add_node("Supplier", initial_stock=2000)
    network.add_node("Warehouse", initial_stock=300)

    supplier_data = {
        "supplier_id": 2,
        "supplier_reliability": 0.88,
        "expected_lead_time": 8,
        "distance_km": 1200,
        "order_quantity": 500,
        "weather_severity": 2,
        "traffic_level": 3,
    }

    prediction = predict_supplier_delay(**supplier_data)

    delay_probability = prediction["delay_probability"]
    predicted_delayed = prediction["predicted_delayed"]

    base_lead_time = supplier_data["expected_lead_time"]

    # Initial deterministic delay scenario
    additional_delay = 3 if predicted_delayed else 0
    actual_lead_time = base_lead_time + additional_delay

    print("\nML SUPPLIER DELAY DIGITAL TWIN")
    print("-" * 65)
    print(f"Supplier ID: {supplier_data['supplier_id']}")
    print(f"Predicted Delay Probability: {delay_probability:.2%}")
    print(f"Risk Level: {prediction['risk_level']}")
    print(f"Predicted Delayed: {predicted_delayed}")
    print(f"Base Lead Time: {base_lead_time} days")
    print(f"Additional Delay: {additional_delay} days")
    print(f"Simulated Lead Time: {actual_lead_time} days")

    env.process(
        network.transfer_stock(
            source="Supplier",
            destination="Warehouse",
            quantity=supplier_data["order_quantity"],
            lead_time=actual_lead_time,
        )
    )

    env.run(until=actual_lead_time + 1)

    print("\nSIMULATION RESULTS")
    print("-" * 65)

    for name, node in network.nodes.items():
        print(f"{name} Final Stock: {node.stock}")

    for shipment in network.shipments:
        print(shipment)


if __name__ == "__main__":
    run_supplier_delay_simulation()
