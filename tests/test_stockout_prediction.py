
from src.ml.stockout_prediction import calculate_stockout_risk


def test_high_stockout_risk():
    risk, ratio = calculate_stockout_risk(
        current_stock=40,
        predicted_daily_demand=20,
        lead_time=5
    )

    assert risk == "HIGH"
    assert ratio == 0.4


def test_medium_stockout_risk():
    risk, ratio = calculate_stockout_risk(
        current_stock=80,
        predicted_daily_demand=20,
        lead_time=5
    )

    assert risk == "MEDIUM"
    assert ratio == 0.8


def test_low_stockout_risk():
    risk, ratio = calculate_stockout_risk(
        current_stock=150,
        predicted_daily_demand=20,
        lead_time=5
    )

    assert risk == "LOW"
    assert ratio == 1.5


def test_zero_demand():
    risk, ratio = calculate_stockout_risk(
        current_stock=100,
        predicted_daily_demand=0,
        lead_time=5
    )

    assert risk == "LOW"
    assert ratio == 0.0


def test_risk_boundaries():
    risk, ratio = calculate_stockout_risk(50, 20, 5)
    assert risk == "MEDIUM"
    assert ratio == 0.5

    risk, ratio = calculate_stockout_risk(100, 20, 5)
    assert risk == "LOW"
    assert ratio == 1.0
