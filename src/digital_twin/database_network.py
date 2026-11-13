
import simpy

from src.digital_twin.network import SupplyChainNetwork
from src.digital_twin.load_network_data import load_supply_chain_data


def create_database_network(product_id=1):
    data = load_supply_chain_data(product_id)

    env = simpy.Environment()
    network = SupplyChainNetwork(env)

    supplier = data["supplier"]

    # Supplier stock is not stored in the inventory table.
    # Use zero as a placeholder until supplier capacity
    # and available stock are modeled separately.
    supplier_name = f"Supplier_{supplier['id']}"

    network.add_node(
        supplier_name,
        initial_stock=0,
    )

    for warehouse in data["warehouses"]:
        stock = sum(
            record["quantity"]
            for record in data["inventory"]
            if record["warehouse_id"] == warehouse["id"]
        )

        network.add_node(
            f"Warehouse_{warehouse['id']}",
            initial_stock=stock,
        )

    for retailer in data["retailers"]:
        stock = sum(
            record["quantity"]
            for record in data["inventory"]
            if record["retailer_id"] == retailer["id"]
        )

        network.add_node(
            f"Retailer_{retailer['id']}",
            initial_stock=stock,
        )

    return env, network, data


def run_database_network():
    env, network, data = create_database_network(
        product_id=1
    )

    print("\nDATABASE-DRIVEN SUPPLY CHAIN DIGITAL TWIN")
    print("-" * 65)

    print(f"Product: {data['product']['name']}")
    print(f"Supplier: {data['supplier']['name']}")

    print("\nINITIAL NETWORK INVENTORY")
    print("-" * 65)

    for name, node in network.nodes.items():
        print(f"{name}: {node.stock} units")

    total_inventory = sum(
        node.stock for node in network.nodes.values()
    )

    print("-" * 65)
    print(f"Total Inventory: {total_inventory} units")
    print(f"Simulation Time: {env.now}")


if __name__ == "__main__":
    run_database_network()
