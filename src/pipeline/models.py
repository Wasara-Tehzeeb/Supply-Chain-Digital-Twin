"""Custom estimators (kept in a module so MLflow-pickled models can be reloaded)."""
from __future__ import annotations

from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.ensemble import RandomForestRegressor


class ResidualForestRegressor(BaseEstimator, RegressorMixin):
    """Random Forest that predicts the deviation from a trailing-mean anchor.

    Tree models cannot extrapolate a trend beyond the training range. Learning
    y - anchor (anchor = rolling_mean_7, computed from PAST data only) removes
    the level/trend, so the forest only models weekday/product effects.
    predict() returns the actual demand (anchor + predicted deviation).
    """

    def __init__(self, anchor="rolling_mean_7", n_estimators=100, max_depth=None,
                 min_samples_leaf=1, random_state=42):
        self.anchor = anchor
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.min_samples_leaf = min_samples_leaf
        self.random_state = random_state

    def fit(self, X, y):
        self.forest_ = RandomForestRegressor(
            n_estimators=self.n_estimators, max_depth=self.max_depth,
            min_samples_leaf=self.min_samples_leaf,
            random_state=self.random_state, n_jobs=1,
        ).fit(X, y - X[self.anchor])
        return self

    def predict(self, X):
        return self.forest_.predict(X) + X[self.anchor].values
