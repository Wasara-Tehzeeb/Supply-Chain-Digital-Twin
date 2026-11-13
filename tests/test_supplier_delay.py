
import pytest

from src.ml.predict_supplier_delay import predict_supplier_delay


@pytest.fixture(scope="module")
def prediction():
    return predict_supplier_delay(
        supplier_id=1,
        supplier_reliability=0.95,
        expected_lead_time=5,
        distance_km=300,
        order_quantity=100,
        weather_severity=0,
        traffic_level=1,
    )


def test_probability_range(prediction):
    assert 0 <= prediction["delay_probability"] <= 1


def test_risk_level(prediction):
    assert prediction["risk_level"] in [
        "LOW",
        "MEDIUM",
        "HIGH",
    ]


def test_prediction_type(prediction):
    assert isinstance(prediction["predicted_delayed"], bool)


def test_risk_classification(prediction):
    probability = prediction["delay_probability"]
    risk = prediction["risk_level"]

    if probability >= 0.7:
        assert risk == "HIGH"
    elif probability >= 0.4:
        assert risk == "MEDIUM"
    else:
        assert risk == "LOW"


def test_binary_prediction(prediction):
    probability = prediction["delay_probability"]

    assert prediction["predicted_delayed"] == (
        probability >= 0.5
    )
