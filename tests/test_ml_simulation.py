
import simpy
import pytest

from src.ml.predict_demand import predict_demand
from src.digital_twin.network import SupplyChainNetwork
from src.digital_twin.auto_replenishment import AutomaticReplenishment
from src.digital_twin.warehouse_replenishment import WarehouseReplenishment


@pytest.fixture(scope="module")
def predicted_demand():
    prediction = predict_demand(
        product_id=1,
        retailer_id=1,
    )
    return max(0, round(float(prediction)))


@pytest.fixture
def simulation(predicted_demand):
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
        daily_demand=predicted_demand,
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


def test_ml_prediction_is_nonnegative(predicted_demand):
    assert predicted_demand >= 0


def test_ml_prediction_is_integer(predicted_demand):
    assert isinstance(predicted_demand, int)


def test_simulation_uses_ml_demand(simulation, predicted_demand):
    env, network, retailer = simulation

    env.run(until=20)

    assert retailer.total_demand == predicted_demand * 20


def test_fulfilled_demand_never_exceeds_total(simulation):
    env, network, retailer = simulation

    env.run(until=20)

    assert 0 <= retailer.total_fulfilled <= retailer.total_demand


def test_inventory_conservation(simulation):
    env, network, retailer = simulation

    initial_stock = sum(
        node.stock for node in network.nodes.values()
    )

    env.run(until=20)

    final_stock = sum(
        node.stock for node in network.nodes.values()
    )

    in_transit = sum(
        shipment["shipped_quantity"]
        for shipment in network.shipments
        if shipment["status"] == "IN_TRANSIT"
    )

    assert (
        initial_stock
        == final_stock + in_transit + retailer.total_fulfilled
    )


def test_no_negative_inventory(simulation):
    env, network, retailer = simulation

    env.run(until=20)

    assert all(
        node.stock >= 0
        for node in network.nodes.values()
    )
