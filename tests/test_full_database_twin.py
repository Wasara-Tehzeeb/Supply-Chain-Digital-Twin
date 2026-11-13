
import pytest

from src.ml.predict_demand import predict_demand
from src.digital_twin.database_network import create_database_network
from src.digital_twin.auto_replenishment import AutomaticReplenishment
from src.digital_twin.warehouse_replenishment import WarehouseReplenishment


@pytest.fixture(scope="module")
def simulation_results():
    env, network, data = create_database_network(product_id=1)

    supplier = data["supplier"]
    supplier_name = f"Supplier_{supplier['id']}"

    network.nodes[supplier_name].receive_stock(5000)

    initial_inventory = sum(
        node.stock for node in network.nodes.values()
    )

    for warehouse in data["warehouses"]:
        warehouse_id = warehouse["id"]

        record = next(
            item for item in data["inventory"]
            if item["warehouse_id"] == warehouse_id
        )

        process = WarehouseReplenishment(
            env=env,
            network=network,
            supplier=supplier_name,
            warehouse=f"Warehouse_{warehouse_id}",
            reorder_point=record["reorder_point"],
            reorder_quantity=500,
            lead_time=supplier["lead_time"],
        )

        env.process(process.monitor_warehouse())

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

        process = AutomaticReplenishment(
            env=env,
            network=network,
            warehouse=f"Warehouse_{retailer_id}",
            retailer=f"Retailer_{retailer_id}",
            daily_demand=daily_demand,
            reorder_point=record["reorder_point"],
            reorder_quantity=150,
            lead_time=3,
        )

        env.process(process.monitor_inventory())
        retailers.append(process)

    env.run(until=30)

    return {
        "network": network,
        "retailers": retailers,
        "initial_inventory": initial_inventory,
        "supplier_lead_time": supplier["lead_time"],
    }


def test_network_has_seven_nodes(simulation_results):
    assert len(simulation_results["network"].nodes) == 7


def test_all_retailers_generate_demand(simulation_results):
    assert all(
        retailer.total_demand > 0
        for retailer in simulation_results["retailers"]
    )


def test_fulfillment_never_exceeds_demand(simulation_results):
    for retailer in simulation_results["retailers"]:
        assert (
            0 <= retailer.total_fulfilled
            <= retailer.total_demand
        )


def test_supplier_replenishment_occurs(simulation_results):
    shipments = simulation_results["network"].shipments

    assert any(
        shipment["source"] == "Supplier_1"
        for shipment in shipments
    )


def test_supplier_lead_time(simulation_results):
    shipments = simulation_results["network"].shipments
    expected = simulation_results["supplier_lead_time"]

    supplier_shipments = [
        shipment for shipment in shipments
        if shipment["source"] == "Supplier_1"
        and shipment["status"] == "DELIVERED"
    ]

    assert supplier_shipments

    for shipment in supplier_shipments:
        assert (
            shipment["arrival_day"] - shipment["departure_day"]
            == expected
        )


def test_inventory_conservation(simulation_results):
    network = simulation_results["network"]

    final_inventory = sum(
        node.stock for node in network.nodes.values()
    )

    fulfilled = sum(
        retailer.total_fulfilled
        for retailer in simulation_results["retailers"]
    )

    in_transit = sum(
        shipment["shipped_quantity"]
        for shipment in network.shipments
        if shipment["status"] == "IN_TRANSIT"
    )

    assert (
        simulation_results["initial_inventory"]
        == final_inventory + fulfilled + in_transit
    )


def test_no_negative_inventory(simulation_results):
    assert all(
        node.stock >= 0
        for node in simulation_results["network"].nodes.values()
    )
