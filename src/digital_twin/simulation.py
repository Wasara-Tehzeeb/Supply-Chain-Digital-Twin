
import simpy


class InventorySimulation:
    def __init__(
        self,
        env,
        initial_stock,
        daily_demand,
        reorder_point,
        reorder_quantity,
        lead_time,
    ):
        self.env = env
        self.stock = initial_stock
        self.daily_demand = daily_demand
        self.reorder_point = reorder_point
        self.reorder_quantity = reorder_quantity
        self.lead_time = lead_time

        self.pending_order = False
        self.total_demand = 0
        self.total_fulfilled = 0
        self.total_stockouts = 0

    def consume_inventory(self):
        while True:
            demand = self.daily_demand
            fulfilled = min(self.stock, demand)

            self.stock -= fulfilled
            self.total_demand += demand
            self.total_fulfilled += fulfilled

            if fulfilled < demand:
                self.total_stockouts += 1

            print(
                f"Day {self.env.now:.0f} | "
                f"Demand: {demand} | "
                f"Fulfilled: {fulfilled} | "
                f"Remaining Stock: {self.stock}"
            )

            if (
                self.stock <= self.reorder_point
                and not self.pending_order
            ):
                self.pending_order = True
                self.env.process(self.replenish_inventory())

            yield self.env.timeout(1)

    def replenish_inventory(self):
        print(
            f"Day {self.env.now:.0f} | "
            f"Replenishment ordered: {self.reorder_quantity}"
        )

        yield self.env.timeout(self.lead_time)

        self.stock += self.reorder_quantity
        self.pending_order = False

        print(
            f"Day {self.env.now:.0f} | "
            f"Shipment arrived | "
            f"New Stock: {self.stock}"
        )


def run_simulation():
    env = simpy.Environment()

    simulation = InventorySimulation(
        env=env,
        initial_stock=100,
        daily_demand=25,
        reorder_point=40,
        reorder_quantity=150,
        lead_time=3,
    )

    env.process(simulation.consume_inventory())

    print("\nSUPPLY CHAIN DIGITAL TWIN SIMULATION")
    print("-" * 60)

    env.run(until=15)

    fulfillment_rate = (
        simulation.total_fulfilled / simulation.total_demand * 100
        if simulation.total_demand > 0
        else 0
    )

    print("\nSIMULATION RESULTS")
    print("-" * 60)
    print(f"Total Demand: {simulation.total_demand}")
    print(f"Total Fulfilled: {simulation.total_fulfilled}")
    print(f"Stockout Days: {simulation.total_stockouts}")
    print(f"Fulfillment Rate: {fulfillment_rate:.2f}%")
    print(f"Final Inventory: {simulation.stock}")


if __name__ == "__main__":
    run_simulation()
