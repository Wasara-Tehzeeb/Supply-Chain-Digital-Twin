
import simpy
import pytest

from src.ml.predict_demand import predict_demand
from src.digital_twin.database_network import create_database_network
from src.digital_twin.auto_replenishment import AutomaticReplenishment


@pytest.fixture(scope="module")
def simulation_results():
    env, network, data = create_database_network(product_id=1)

    initial_inventory = sum(
        node.stock for node in network.nodes.values()
    )

    retailers = []

    for retailer in data["retailers"]:
        retailer_id = retailer["id"]

        record = next(
            item for item in data["inventory"]
            if item["retailer_id"] == retailer_id
        )

        daily_demand = max(
            0,
            round(float(predict_demand(
                product_id=1,
                retailer_id=retailer_id,
            ))),
        )

        replenishment = AutomaticReplenishment(
            env=env,
            network=network,
            warehouse=f"Warehouse_{retailer_id}",
            retailer=f"Retailer_{retailer_id}",
            daily_demand=daily_demand,
            reorder_point=record["reorder_point"],
            reorder_quantity=150,
            lead_time=3,
        )

        env.process(replenishment.monitor_inventory())
        retailers.append(replenishment)

    env.run(until=20)

    return {
        "network": network,
        "retailers": retailers,
        "initial_inventory": initial_inventory,
    }


def test_network_contains_all_locations(simulation_results):
    network = simulation_results["network"]

    assert len(network.nodes) == 7
    assert "Supplier_1" in network.nodes
    assert all(
        f"Warehouse_{i}" in network.nodes
        for i in range(1, 4)
    )
    assert all(
        f"Retailer_{i}" in network.nodes
        for i in range(1, 4)
    )


def test_all_retailers_have_demand(simulation_results):
    retailers = simulation_results["retailers"]

    assert len(retailers) == 3
    assert all(
        retailer.total_demand > 0
        for retailer in retailers
    )


def test_demand_fulfillment_bounds(simulation_results):
    for retailer in simulation_results["retailers"]:
        assert (
            0 <= retailer.total_fulfilled
            <= retailer.total_demand
        )


def test_all_shipments_delivered(simulation_results):
    network = simulation_results["network"]

    assert len(network.shipments) > 0
    assert all(
        shipment["status"] == "DELIVERED"
        for shipment in network.shipments
    )


def test_inventory_conservation(simulation_results):
    network = simulation_results["network"]
    retailers = simulation_results["retailers"]

    initial = simulation_results["initial_inventory"]

    final = sum(
        node.stock for node in network.nodes.values()
    )

    fulfilled = sum(
        retailer.total_fulfilled
        for retailer in retailers
    )

    in_transit = sum(
        shipment["shipped_quantity"]
        for shipment in network.shipments
        if shipment["status"] == "IN_TRANSIT"
    )

    assert initial == final + fulfilled + in_transit


def test_no_negative_inventory(simulation_results):
    network = simulation_results["network"]

    assert all(
        node.stock >= 0
        for node in network.nodes.values()
    )


def test_supplier_inventory_unchanged(simulation_results):
    network = simulation_results["network"]

    assert network.nodes["Supplier_1"].stock == 0
