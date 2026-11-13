
import simpy

from src.digital_twin.network import SupplyChainNetwork


class AutomaticReplenishment:
    def __init__(
        self,
        env,
        network,
        warehouse,
        retailer,
        daily_demand,
        reorder_point,
        reorder_quantity,
        lead_time,
    ):
        self.env = env
        self.network = network
        self.warehouse = warehouse
        self.retailer = retailer
        self.daily_demand = daily_demand
        self.reorder_point = reorder_point
        self.reorder_quantity = reorder_quantity
        self.lead_time = lead_time

        self.pending_order = False
        self.total_demand = 0
        self.total_fulfilled = 0
        self.stockout_days = 0

    def monitor_inventory(self):
        while True:
            retailer_node = self.network.nodes[self.retailer]

            demand = self.daily_demand
            fulfilled = retailer_node.send_stock(demand)

            self.total_demand += demand
            self.total_fulfilled += fulfilled

            if fulfilled < demand:
                self.stockout_days += 1

            print(
                f"Day {self.env.now:.0f} | "
                f"Retailer demand: {demand} | "
                f"Fulfilled: {fulfilled} | "
                f"Stock: {retailer_node.stock}"
            )

            if (
                retailer_node.stock <= self.reorder_point
                and not self.pending_order
            ):
                self.pending_order = True
                self.env.process(self.place_replenishment_order())

            yield self.env.timeout(1)

    def place_replenishment_order(self):
        shipment_process = self.env.process(
            self.network.transfer_stock(
                source=self.warehouse,
                destination=self.retailer,
                quantity=self.reorder_quantity,
                lead_time=self.lead_time,
            )
        )

        yield shipment_process

        self.pending_order = False


def run_auto_replenishment():
    env = simpy.Environment()
    network = SupplyChainNetwork(env)

    network.add_node("Supplier", initial_stock=1000)
    network.add_node("Warehouse", initial_stock=500)
    network.add_node("Retailer", initial_stock=100)

    replenishment = AutomaticReplenishment(
        env=env,
        network=network,
        warehouse="Warehouse",
        retailer="Retailer",
        daily_demand=25,
        reorder_point=40,
        reorder_quantity=150,
        lead_time=3,
    )

    env.process(replenishment.monitor_inventory())

    print("\nAUTOMATIC REPLENISHMENT SIMULATION")
    print("-" * 65)

    env.run(until=15)

    print("\nSIMULATION RESULTS")
    print("-" * 65)

    print(f"Total Demand: {replenishment.total_demand}")
    print(f"Total Fulfilled: {replenishment.total_fulfilled}")
    print(f"Stockout Days: {replenishment.stockout_days}")

    fulfillment_rate = (
        replenishment.total_fulfilled
        / replenishment.total_demand
        * 100
        if replenishment.total_demand > 0
        else 0
    )

    print(f"Fulfillment Rate: {fulfillment_rate:.2f}%")

    for name, node in network.nodes.items():
        print(f"{name} Final Stock: {node.stock}")

    print("\nSHIPMENT SUMMARY")

    for shipment in network.shipments:
        print(shipment)


if __name__ == "__main__":
    run_auto_replenishment()
