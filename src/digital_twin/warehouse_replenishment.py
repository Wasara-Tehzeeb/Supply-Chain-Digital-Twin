
import simpy

from src.digital_twin.network import SupplyChainNetwork
from src.digital_twin.auto_replenishment import AutomaticReplenishment


class WarehouseReplenishment:
    def __init__(
        self,
        env,
        network,
        supplier,
        warehouse,
        reorder_point,
        reorder_quantity,
        lead_time,
    ):
        self.env = env
        self.network = network
        self.supplier = supplier
        self.warehouse = warehouse
        self.reorder_point = reorder_point
        self.reorder_quantity = reorder_quantity
        self.lead_time = lead_time

        self.pending_order = False

    def monitor_warehouse(self):
        while True:
            warehouse_node = self.network.nodes[self.warehouse]

            if (
                warehouse_node.stock <= self.reorder_point
                and not self.pending_order
            ):
                self.pending_order = True

                self.env.process(
                    self.place_supplier_order()
                )

            yield self.env.timeout(1)

    def place_supplier_order(self):
        print(
            f"Day {self.env.now:.0f} | "
            f"Warehouse replenishment triggered"
        )

        shipment = self.env.process(
            self.network.transfer_stock(
                source=self.supplier,
                destination=self.warehouse,
                quantity=self.reorder_quantity,
                lead_time=self.lead_time,
            )
        )

        yield shipment

        self.pending_order = False


def run_full_supply_chain():
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
        daily_demand=25,
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

    print("\nFULL SUPPLY CHAIN DIGITAL TWIN")
    print("-" * 65)

    env.run(until=20)

    print("\nFINAL RESULTS")
    print("-" * 65)

    print(f"Total Demand: {retailer_replenishment.total_demand}")
    print(f"Fulfilled Demand: {retailer_replenishment.total_fulfilled}")
    print(f"Stockout Days: {retailer_replenishment.stockout_days}")

    fulfillment_rate = (
        retailer_replenishment.total_fulfilled
        / retailer_replenishment.total_demand
        * 100
        if retailer_replenishment.total_demand > 0
        else 0
    )

    print(f"Fulfillment Rate: {fulfillment_rate:.2f}%")

    for name, node in network.nodes.items():
        print(f"{name} Final Stock: {node.stock}")

    print("\nSHIPMENT SUMMARY")

    for shipment in network.shipments:
        print(shipment)


if __name__ == "__main__":
    run_full_supply_chain()
