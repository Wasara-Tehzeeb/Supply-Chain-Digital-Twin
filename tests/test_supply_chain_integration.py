
import simpy

from src.digital_twin.network import SupplyChainNetwork
from src.digital_twin.auto_replenishment import AutomaticReplenishment
from src.digital_twin.warehouse_replenishment import WarehouseReplenishment


def create_full_simulation():
    env = simpy.Environment()
    network = SupplyChainNetwork(env)

    network.add_node("Supplier", initial_stock=2000)
    network.add_node("Warehouse", initial_stock=300)
    network.add_node("Retailer", initial_stock=100)

    retailer = AutomaticReplenishment(
        env=env,
        network=network,
        warehouse="Warehouse",
        retailer="Retailer",
        daily_demand=25,
        reorder_point=40,
        reorder_quantity=150,
        lead_time=3,
    )

    warehouse = WarehouseReplenishment(
        env=env,
        network=network,
        supplier="Supplier",
        warehouse="Warehouse",
        reorder_point=200,
        reorder_quantity=500,
        lead_time=4,
    )

    env.process(retailer.monitor_inventory())
    env.process(warehouse.monitor_warehouse())

    return env, network, retailer


def test_complete_supply_chain():
    env, network, retailer = create_full_simulation()

    env.run(until=20)

    assert retailer.total_demand == 500
    assert retailer.total_fulfilled == 425
    assert retailer.stockout_days == 3

    assert network.nodes["Supplier"].stock == 1500
    assert network.nodes["Warehouse"].stock == 350
    assert network.nodes["Retailer"].stock == 125


def test_all_shipments_delivered():
    env, network, _ = create_full_simulation()

    env.run(until=20)

    assert len(network.shipments) == 4
    assert all(
        shipment["status"] == "DELIVERED"
        for shipment in network.shipments
    )


def test_no_negative_inventory():
    env, network, _ = create_full_simulation()

    env.run(until=20)

    assert all(
        node.stock >= 0
        for node in network.nodes.values()
    )


def test_inventory_conservation_with_consumption():
    env, network, retailer = create_full_simulation()

    initial_inventory = sum(
        node.stock for node in network.nodes.values()
    )

    env.run(until=20)

    final_inventory = sum(
        node.stock for node in network.nodes.values()
    )

    assert (
        initial_inventory
        == final_inventory + retailer.total_fulfilled
    )


def test_fulfillment_rate():
    env, network, retailer = create_full_simulation()

    env.run(until=20)

    fulfillment_rate = (
        retailer.total_fulfilled
        / retailer.total_demand
        * 100
    )

    assert fulfillment_rate == 85.0
