import pandas as pd
import pytest
from datetime import date

from src.pipeline.generate_data import generate_demand
from src.pipeline.models import ResidualForestRegressor
from src.pipeline.prepare import (
    assert_no_leakage, build_demand_features, time_split_by_key,
)


@pytest.fixture
def feats():
    return build_demand_features(generate_demand(60, date(2026, 1, 1)))


def test_splits_are_strictly_time_ordered(feats):
    tr, va, te = time_split_by_key(feats, "demand_date", 0.7, 0.15)
    assert_no_leakage(tr, va, te, "demand_date")
    assert tr["demand_date"].max() < va["demand_date"].min()
    assert va["demand_date"].max() < te["demand_date"].min()
    assert len(tr) + len(va) + len(te) == len(feats)  # nothing dropped or duplicated


def test_overlap_is_caught(feats):
    tr, va, te = time_split_by_key(feats, "demand_date", 0.7, 0.15)
    with pytest.raises(AssertionError):
        assert_no_leakage(tr, pd.concat([va, tr.tail(5)]), te, "demand_date")


def test_features_only_use_past(feats):
    """Changing FUTURE targets must not change features of earlier rows."""
    raw = generate_demand(60, date(2026, 1, 1))
    base = build_demand_features(raw)
    mutated = raw.copy()
    cutoff = "2026-02-15"
    mutated.loc[mutated["demand_date"] > cutoff, "quantity_sold"] += 1000
    alt = build_demand_features(mutated)
    cols = ["lag_1", "lag_7", "rolling_mean_7"]
    early_a = base[base["demand_date"].astype(str) <= cutoff][cols].reset_index(drop=True)
    early_b = alt[alt["demand_date"].astype(str) <= cutoff][cols].reset_index(drop=True)
    pd.testing.assert_frame_equal(early_a, early_b)


def test_residual_forest_predicts_actual_scale(feats):
    X = feats[["rolling_mean_7", "day_of_week"]]
    y = feats["quantity_sold"]
    m = ResidualForestRegressor("rolling_mean_7", 20, 3, 5, 0).fit(X, y)
    assert abs(m.predict(X).mean() - y.mean()) < 3


def test_pipeline_is_deterministic():
    a = build_demand_features(generate_demand(40, date(2026, 1, 1)))
    b = build_demand_features(generate_demand(40, date(2026, 1, 1)))
    pd.testing.assert_frame_equal(a, b)
