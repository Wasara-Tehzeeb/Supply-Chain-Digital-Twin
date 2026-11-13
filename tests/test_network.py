
import pytest
import simpy

from src.digital_twin.network import (
    SupplyChainNode,
    SupplyChainNetwork,
)


def test_receive_stock():
    node = SupplyChainNode("Warehouse", 100)

    node.receive_stock(50)

    assert node.stock == 150
    assert node.total_received == 50


def test_send_stock():
    node = SupplyChainNode("Warehouse", 100)

    shipped = node.send_stock(40)

    assert shipped == 40
    assert node.stock == 60
    assert node.total_sent == 40


def test_insufficient_stock():
    node = SupplyChainNode("Warehouse", 50)

    shipped = node.send_stock(100)

    assert shipped == 50
    assert node.stock == 0


def test_negative_quantity():
    node = SupplyChainNode("Warehouse", 100)

    with pytest.raises(ValueError):
        node.receive_stock(-10)

    with pytest.raises(ValueError):
        node.send_stock(-10)


def test_duplicate_node():
    env = simpy.Environment()
    network = SupplyChainNetwork(env)

    network.add_node("Supplier", 100)

    with pytest.raises(ValueError):
        network.add_node("Supplier", 200)


def test_shipment_delivery():
    env = simpy.Environment()
    network = SupplyChainNetwork(env)

    network.add_node("Supplier", 500)
    network.add_node("Warehouse", 100)

    env.process(
        network.transfer_stock(
            source="Supplier",
            destination="Warehouse",
            quantity=200,
            lead_time=3,
        )
    )

    env.run(until=4)

    assert network.nodes["Supplier"].stock == 300
    assert network.nodes["Warehouse"].stock == 300
    assert network.shipments[0]["status"] == "DELIVERED"
    assert network.shipments[0]["arrival_day"] == 3


def test_inventory_conservation():
    env = simpy.Environment()
    network = SupplyChainNetwork(env)

    network.add_node("Supplier", 1000)
    network.add_node("Warehouse", 200)
    network.add_node("Retailer", 50)

    initial_total = sum(
        node.stock for node in network.nodes.values()
    )

    env.process(
        network.transfer_stock(
            "Supplier", "Warehouse", 300, 3
        )
    )

    env.process(
        network.transfer_stock(
            "Warehouse", "Retailer", 100, 2
        )
    )

    env.run(until=5)

    final_total = sum(
        node.stock for node in network.nodes.values()
    )

    assert initial_total == final_total
    assert final_total == 1250
