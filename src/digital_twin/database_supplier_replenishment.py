
import simpy

from src.digital_twin.database_network import create_database_network
from src.digital_twin.warehouse_replenishment import WarehouseReplenishment


def run_supplier_replenishment():
    env, network, data = create_database_network(product_id=1)

    supplier = data["supplier"]
    supplier_name = f"Supplier_{supplier['id']}"

    # Simulation-only supplier inventory.
    # PostgreSQL supplier inventory is not modified.
    network.nodes[supplier_name].receive_stock(5000)

    warehouse_processes = []

    print("\nDATABASE-DRIVEN SUPPLIER REPLENISHMENT")
    print("-" * 65)
    print(f"Product: {data['product']['name']}")
    print(f"Supplier: {supplier['name']}")
    print(f"Supplier Lead Time: {supplier['lead_time']} days")

    for warehouse in data["warehouses"]:
        warehouse_id = warehouse["id"]
        warehouse_name = f"Warehouse_{warehouse_id}"

        inventory_record = next(
            record
            for record in data["inventory"]
            if record["warehouse_id"] == warehouse_id
        )

        replenishment = WarehouseReplenishment(
            env=env,
            network=network,
            supplier=supplier_name,
            warehouse=warehouse_name,
            reorder_point=inventory_record["reorder_point"],
            reorder_quantity=500,
            lead_time=supplier["lead_time"],
        )

        env.process(replenishment.monitor_warehouse())
        warehouse_processes.append(replenishment)

        print(
            f"{warehouse_name} | "
            f"Initial Stock: {network.nodes[warehouse_name].stock} | "
            f"Reorder Point: {inventory_record['reorder_point']}"
        )

    print("-" * 65)

    # Simulate retailer orders that reduce warehouse stock.
    def simulate_warehouse_demand():
        yield env.timeout(1)

        for warehouse in data["warehouses"]:
            warehouse_name = f"Warehouse_{warehouse['id']}"

            shipped = network.nodes[warehouse_name].send_stock(400)

            print(
                f"Day {env.now:.0f} | "
                f"{warehouse_name} dispatched {shipped} units"
            )

    env.process(simulate_warehouse_demand())

    env.run(until=10)

    print("\nFINAL INVENTORY")
    print("-" * 65)

    for name, node in network.nodes.items():
        print(f"{name}: {node.stock} units")

    print("\nSUPPLIER SHIPMENTS")

    for shipment in network.shipments:
        print(shipment)


if __name__ == "__main__":
    run_supplier_replenishment()
