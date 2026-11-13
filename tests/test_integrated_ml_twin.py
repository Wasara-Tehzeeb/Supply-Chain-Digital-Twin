
import pytest
import simpy

from src.ml.predict_demand import predict_demand
from src.ml.predict_supplier_delay import predict_supplier_delay
from src.digital_twin.network import SupplyChainNetwork
from src.digital_twin.auto_replenishment import AutomaticReplenishment
from src.digital_twin.warehouse_replenishment import WarehouseReplenishment


@pytest.fixture(scope="module")
def ml_inputs():
    demand = max(
        0,
        round(float(predict_demand(product_id=1, retailer_id=1))),
    )

    delay = predict_supplier_delay(
        supplier_id=2,
        supplier_reliability=0.88,
        expected_lead_time=8,
        distance_km=1200,
        order_quantity=500,
        weather_severity=2,
        traffic_level=3,
    )

    lead_time = 8 + (3 if delay["predicted_delayed"] else 0)

    return demand, delay, lead_time


@pytest.fixture
def simulation(ml_inputs):
    demand, delay, lead_time = ml_inputs

    env = simpy.Environment()
    network = SupplyChainNetwork(env)

    network.add_node("Supplier", 2000)
    network.add_node("Warehouse", 300)
    network.add_node("Retailer", 100)

    retailer = AutomaticReplenishment(
        env=env,
        network=network,
        warehouse="Warehouse",
        retailer="Retailer",
        daily_demand=demand,
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
        lead_time=lead_time,
    )

    env.process(retailer.monitor_inventory())
    env.process(warehouse.monitor_warehouse())

    return env, network, retailer


def test_demand_prediction(ml_inputs):
    demand, _, _ = ml_inputs

    assert isinstance(demand, int)
    assert demand >= 0


def test_supplier_delay_prediction(ml_inputs):
    _, delay, lead_time = ml_inputs

    assert 0 <= delay["delay_probability"] <= 1
    assert lead_time in (8, 11)


def test_integrated_demand(simulation, ml_inputs):
    env, network, retailer = simulation
    demand, _, _ = ml_inputs

    env.run(until=30)

    assert retailer.total_demand == demand * 30


def test_fulfillment_bounds(simulation):
    env, network, retailer = simulation

    env.run(until=30)

    assert 0 <= retailer.total_fulfilled <= retailer.total_demand


def test_inventory_conservation_with_in_transit(simulation):
    env, network, retailer = simulation

    initial_inventory = sum(
        node.stock for node in network.nodes.values()
    )

    env.run(until=30)

    final_inventory = sum(
        node.stock for node in network.nodes.values()
    )

    in_transit = sum(
        shipment["shipped_quantity"]
        for shipment in network.shipments
        if shipment["status"] == "IN_TRANSIT"
    )

    assert initial_inventory == (
        final_inventory
        + in_transit
        + retailer.total_fulfilled
    )


def test_no_negative_inventory(simulation):
    env, network, retailer = simulation

    env.run(until=30)

    assert all(
        node.stock >= 0
        for node in network.nodes.values()
    )


def test_supplier_shipments_use_ml_lead_time(simulation, ml_inputs):
    env, network, retailer = simulation
    _, _, expected_lead_time = ml_inputs

    env.run(until=30)

    supplier_shipments = [
        shipment
        for shipment in network.shipments
        if shipment["source"] == "Supplier"
    ]

    assert len(supplier_shipments) >= 1

    for shipment in supplier_shipments:
        if shipment["status"] == "DELIVERED":
            actual_lead_time = (
                shipment["arrival_day"]
                - shipment["departure_day"]
            )

            assert actual_lead_time == expected_lead_time
