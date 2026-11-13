
from src.inventory.replenishment import calculate_reorder_quantity


def test_reorder_required():
    result = calculate_reorder_quantity(
        current_stock=100,
        daily_demand=30,
        lead_time=5,
        safety_stock=20
    )
    assert result == 70


def test_sufficient_stock():
    result = calculate_reorder_quantity(
        current_stock=200,
        daily_demand=20,
        lead_time=5,
        safety_stock=20
    )
    assert result == 0


def test_zero_demand():
    result = calculate_reorder_quantity(
        current_stock=100,
        daily_demand=0,
        lead_time=5,
        safety_stock=20
    )
    assert result == 0


def test_fractional_demand():
    result = calculate_reorder_quantity(
        current_stock=100,
        daily_demand=22.1,
        lead_time=5,
        safety_stock=20
    )
    assert result == 31


def test_critical_inventory():
    result = calculate_reorder_quantity(
        current_stock=10,
        daily_demand=30,
        lead_time=5,
        safety_stock=20
    )
    assert result == 160
