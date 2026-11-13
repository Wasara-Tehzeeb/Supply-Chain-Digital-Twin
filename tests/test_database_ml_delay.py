
import pytest

from src.digital_twin.database_ml_delay import (
    get_ml_supplier_lead_time,
)
from src.digital_twin.database_network import (
    create_database_network,
)
from src.digital_twin.warehouse_replenishment import (
    WarehouseReplenishment,
)


@pytest.fixture(scope="module")
def delay_result():
    return get_ml_supplier_lead_time(product_id=1)


def test_supplier_matches_database(delay_result):
    assert delay_result["supplier_id"] == 1
    assert delay_result["supplier_name"] == "Alpha Manufacturing"


def test_delay_probability_valid(delay_result):
    assert 0 <= delay_result["delay_probability"] <= 1


def test_adjusted_lead_time(delay_result):
    expected = (
        delay_result["base_lead_time"]
        + delay_result["additional_delay"]
    )

    assert delay_result["adjusted_lead_time"] == expected


def test_delay_rule(delay_result):
    if delay_result["predicted_delayed"]:
        assert delay_result["additional_delay"] == 3
    else:
        assert delay_result["additional_delay"] == 0


def test_supplier_shipment_uses_ml_lead_time(delay_result):
    env, network, data = create_database_network(product_id=1)

    supplier_name = f"Supplier_{data['supplier']['id']}"
    network.nodes[supplier_name].receive_stock(1000)

    # Force a warehouse below its database reorder point.
    warehouse = network.nodes["Warehouse_1"]
    warehouse.send_stock(400)

    replenishment = WarehouseReplenishment(
        env=env,
        network=network,
        supplier=supplier_name,
        warehouse="Warehouse_1",
        reorder_point=150,
        reorder_quantity=500,
        lead_time=delay_result["adjusted_lead_time"],
    )

    env.process(replenishment.monitor_warehouse())

    env.run(until=delay_result["adjusted_lead_time"] + 2)

    shipments = [
        shipment
        for shipment in network.shipments
        if shipment["source"] == supplier_name
    ]

    assert len(shipments) == 1

    shipment = shipments[0]

    assert shipment["status"] == "DELIVERED"

    actual_lead_time = (
        shipment["arrival_day"]
        - shipment["departure_day"]
    )

    assert actual_lead_time == delay_result["adjusted_lead_time"]


def test_inventory_conservation_with_ml_delay(delay_result):
    env, network, data = create_database_network(product_id=1)

    supplier_name = f"Supplier_{data['supplier']['id']}"
    network.nodes[supplier_name].receive_stock(1000)

    initial_inventory = sum(
        node.stock for node in network.nodes.values()
    )

    replenishment = WarehouseReplenishment(
        env=env,
        network=network,
        supplier=supplier_name,
        warehouse="Warehouse_1",
        reorder_point=600,
        reorder_quantity=500,
        lead_time=delay_result["adjusted_lead_time"],
    )

    env.process(replenishment.monitor_warehouse())

    env.run(until=5)

    final_inventory = sum(
        node.stock for node in network.nodes.values()
    )

    in_transit = sum(
        shipment["shipped_quantity"]
        for shipment in network.shipments
        if shipment["status"] == "IN_TRANSIT"
    )

    assert initial_inventory == final_inventory + in_transit
