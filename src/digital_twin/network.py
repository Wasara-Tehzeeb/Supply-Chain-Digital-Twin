
import simpy


class SupplyChainNode:
    def __init__(self, name, initial_stock=0):
        self.name = name
        self.stock = initial_stock
        self.total_received = 0
        self.total_sent = 0

    def receive_stock(self, quantity):
        if quantity < 0:
            raise ValueError("Quantity cannot be negative")

        self.stock += quantity
        self.total_received += quantity

    def send_stock(self, quantity):
        if quantity < 0:
            raise ValueError("Quantity cannot be negative")

        shipped = min(self.stock, quantity)
        self.stock -= shipped
        self.total_sent += shipped

        return shipped


class SupplyChainNetwork:
    def __init__(self, env):
        self.env = env
        self.nodes = {}
        self.shipments = []

    def add_node(self, name, initial_stock=0):
        if name in self.nodes:
            raise ValueError(f"Node already exists: {name}")

        if initial_stock < 0:
            raise ValueError("Initial stock cannot be negative")

        self.nodes[name] = SupplyChainNode(
            name,
            initial_stock
        )

    def transfer_stock(
        self,
        source,
        destination,
        quantity,
        lead_time,
    ):
        if source not in self.nodes:
            raise ValueError(f"Unknown source: {source}")

        if destination not in self.nodes:
            raise ValueError(f"Unknown destination: {destination}")

        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        if lead_time < 0:
            raise ValueError("Lead time cannot be negative")

        shipped = self.nodes[source].send_stock(quantity)

        shipment = {
            "source": source,
            "destination": destination,
            "requested_quantity": quantity,
            "shipped_quantity": shipped,
            "status": "IN_TRANSIT",
            "departure_day": self.env.now,
            "arrival_day": None,
        }

        self.shipments.append(shipment)

        print(
            f"Day {self.env.now:.0f} | "
            f"{source} -> {destination} | "
            f"Shipped: {shipped}"
        )

        yield self.env.timeout(lead_time)

        self.nodes[destination].receive_stock(shipped)

        shipment["status"] = "DELIVERED"
        shipment["arrival_day"] = self.env.now

        print(
            f"Day {self.env.now:.0f} | "
            f"Shipment delivered to {destination} | "
            f"Quantity: {shipped}"
        )


def run_network_simulation():
    env = simpy.Environment()
    network = SupplyChainNetwork(env)

    network.add_node("Supplier", initial_stock=1000)
    network.add_node("Warehouse", initial_stock=200)
    network.add_node("Retailer", initial_stock=50)

    env.process(
        network.transfer_stock(
            source="Supplier",
            destination="Warehouse",
            quantity=300,
            lead_time=3,
        )
    )

    env.process(
        network.transfer_stock(
            source="Warehouse",
            destination="Retailer",
            quantity=100,
            lead_time=2,
        )
    )

    print("\nMULTI-ECHELON SUPPLY CHAIN SIMULATION")
    print("-" * 65)

    env.run(until=5)

    print("\nFINAL INVENTORY")
    print("-" * 65)

    for name, node in network.nodes.items():
        print(
            f"{name} | "
            f"Stock: {node.stock} | "
            f"Received: {node.total_received} | "
            f"Sent: {node.total_sent}"
        )

    print("\nSHIPMENT SUMMARY")
    for shipment in network.shipments:
        print(shipment)


if __name__ == "__main__":
    run_network_simulation()
