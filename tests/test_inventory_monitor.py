
from src.inventory.inventory_monitor import get_stock_status


def test_healthy_stock():
    assert get_stock_status(500, 150, 75) == "HEALTHY"


def test_low_stock():
    assert get_stock_status(100, 150, 75) == "LOW STOCK"


def test_critical_stock():
    assert get_stock_status(50, 150, 75) == "CRITICAL"


def test_boundary_values():
    assert get_stock_status(75, 150, 75) == "CRITICAL"
    assert get_stock_status(150, 150, 75) == "LOW STOCK"
    assert get_stock_status(151, 150, 75) == "HEALTHY"
