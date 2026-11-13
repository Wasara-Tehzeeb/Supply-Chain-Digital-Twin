
import pytest
import simpy

from src.ml.predict_supplier_delay import predict_supplier_delay
from src.digital_twin.network import SupplyChainNetwork


@pytest.fixture(scope="module")
def prediction():
    return predict_supplier_delay(
        supplier_id=2,
        supplier_reliability=0.88,
        expected_lead_time=8,
        distance_km=1200,
        order_quantity=500,
        weather_severity=2,
        traffic_level=3,
    )


def calculate_lead_time(base_lead_time, predicted_delayed):
    additional_delay = 3 if predicted_delayed else 0
    return base_lead_time + additional_delay


def test_delay_probability(prediction):
    assert 0 <= prediction["delay_probability"] <= 1


def test_delay_risk_classification(prediction):
    probability = prediction["delay_probability"]

    if probability >= 0.7:
        assert prediction["risk_level"] == "HIGH"
    elif probability >= 0.4:
        assert prediction["risk_level"] == "MEDIUM"
    else:
        assert prediction["risk_level"] == "LOW"


def test_lead_time_calculation():
    assert calculate_lead_time(8, True) == 11
    assert calculate_lead_time(8, False) == 8


def test_shipment_arrival_with_ml_delay(prediction):
    env = simpy.Environment()
    network = SupplyChainNetwork(env)

    network.add_node("Supplier", 2000)
    network.add_node("Warehouse", 300)

    lead_time = calculate_lead_time(
        8,
        prediction["predicted_delayed"],
    )

    env.process(
        network.transfer_stock(
            source="Supplier",
            destination="Warehouse",
            quantity=500,
            lead_time=lead_time,
        )
    )

    env.run(until=lead_time + 1)

    shipment = network.shipments[0]

    assert shipment["status"] == "DELIVERED"
    assert shipment["arrival_day"] == lead_time
    assert network.nodes["Supplier"].stock == 1500
    assert network.nodes["Warehouse"].stock == 800


def test_shipment_in_transit_before_arrival():
    env = simpy.Environment()
    network = SupplyChainNetwork(env)

    network.add_node("Supplier", 1000)
    network.add_node("Warehouse", 100)

    env.process(
        network.transfer_stock(
            source="Supplier",
            destination="Warehouse",
            quantity=200,
            lead_time=5,
        )
    )

    env.run(until=5)

    assert network.shipments[0]["status"] == "IN_TRANSIT"
    assert network.nodes["Warehouse"].stock == 100

    env.run(until=6)

    assert network.shipments[0]["status"] == "DELIVERED"
    assert network.nodes["Warehouse"].stock == 300
