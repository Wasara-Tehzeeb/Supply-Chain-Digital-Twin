import pandas as pd
import pytest

from src.pipeline.generate_data import generate_demand, generate_suppliers
from src.pipeline.validate import validate_demand, validate_file, validate_supplier
from datetime import date


@pytest.fixture
def demand():
    return generate_demand(30, date(2026, 1, 1))


@pytest.fixture
def supplier():
    return generate_suppliers(200, 42)


def test_clean_data_passes(demand, supplier):
    assert validate_demand(demand) == []
    assert validate_supplier(supplier) == []


def test_missing_column_detected(demand):
    assert any("missing columns" in e for e in validate_demand(demand.drop(columns=["quantity_sold"])))


def test_null_detected(demand):
    demand.loc[5, "quantity_sold"] = None
    assert any("null" in e for e in validate_demand(demand))


def test_corrupted_string_detected(demand):
    demand["quantity_sold"] = demand["quantity_sold"].astype(object)
    demand.loc[3, "quantity_sold"] = "N/A"
    assert any("not numeric" in e for e in validate_demand(demand))


def test_bad_date_detected(demand):
    demand.loc[2, "demand_date"] = "not-a-date"
    assert any("demand_date" in e for e in validate_demand(demand))


def test_negative_and_outlier_detected(demand):
    demand.loc[0, "quantity_sold"] = -4
    demand.loc[1, "quantity_sold"] = 99999
    errs = " ".join(validate_demand(demand))
    assert "negative" in errs and "outliers" in errs


def test_duplicates_and_gaps_detected(demand):
    dup = pd.concat([demand, demand.iloc[[0]]])
    assert any("duplicate" in e for e in validate_demand(dup))
    gap = demand.drop(index=10)
    assert any("missing days" in e for e in validate_demand(gap))


def test_supplier_range_and_balance(supplier):
    supplier.loc[0, "weather_severity"] = 9
    assert any("outside" in e for e in validate_supplier(supplier))
    supplier["is_delayed"] = 0
    assert any("class balance" in e for e in validate_supplier(supplier))


def test_file_level_failures(tmp_path):
    missing = validate_file("demand", tmp_path / "nope.csv")
    assert not missing["passed"] and "file not found" in missing["errors"]
    empty = tmp_path / "empty.csv"
    empty.write_text("")
    assert not validate_file("demand", empty)["passed"]
    garbage = tmp_path / "bad.csv"
    garbage.write_text("a,b\n1,2,3,4\n\x00\x00")
    assert not validate_file("supplier", garbage)["passed"]
