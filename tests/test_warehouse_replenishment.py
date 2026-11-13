
import simpy

from src.digital_twin.network import SupplyChainNetwork
from src.digital_twin.warehouse_replenishment import (
    WarehouseReplenishment,
)


def create_simulation(
    supplier_stock=2000,
    warehouse_stock=150,
    reorder_point=200,
    reorder_quantity=500,
    lead_time=4,
):
    env = simpy.Environment()
    network = SupplyChainNetwork(env)

    network.add_node("Supplier", supplier_stock)
    network.add_node("Warehouse", warehouse_stock)

    replenishment = WarehouseReplenishment(
        env=env,
        network=network,
        supplier="Supplier",
        warehouse="Warehouse",
        reorder_point=reorder_point,
        reorder_quantity=reorder_quantity,
        lead_time=lead_time,
    )

    env.process(replenishment.monitor_warehouse())

    return env, network, replenishment


def test_replenishment_trigger():
    env, network, replenishment = create_simulation()

    env.run(until=1)

    assert replenishment.pending_order is True
    assert len(network.shipments) == 1
    assert network.shipments[0]["status"] == "IN_TRANSIT"


def test_supplier_stock_decreases():
    env, network, _ = create_simulation()

    env.run(until=1)

    assert network.nodes["Supplier"].stock == 1500


def test_warehouse_receives_stock():
    env, network, replenishment = create_simulation()

    env.run(until=5)

    assert network.nodes["Warehouse"].stock == 650
    assert replenishment.pending_order is False
    assert network.shipments[0]["status"] == "DELIVERED"
    assert network.shipments[0]["arrival_day"] == 4


def test_no_replenishment_above_threshold():
    env, network, replenishment = create_simulation(
        warehouse_stock=300
    )

    env.run(until=5)

    assert len(network.shipments) == 0
    assert replenishment.pending_order is False


def test_no_duplicate_pending_orders():
    env, network, replenishment = create_simulation()

    env.run(until=3)

    assert len(network.shipments) == 1
    assert replenishment.pending_order is True


def test_inventory_conservation():
    env, network, _ = create_simulation()

    initial_total = sum(
        node.stock for node in network.nodes.values()
    )

    env.run(until=5)

    final_total = sum(
        node.stock for node in network.nodes.values()
    )

    assert initial_total == final_total
