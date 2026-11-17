"""Compare freshly produced metrics with the committed expected ones.

    python -m src.pipeline.reproduce          # exit 0 = reproduced
    python -m src.pipeline.reproduce --update # (re)write expected_metrics.json
"""
from __future__ import annotations

import argparse
import json
import sys

from src.pipeline.config import REPORTS_DIR, load_params

ACTUAL = REPORTS_DIR / "registered_metrics.json"
EXPECTED = REPORTS_DIR / "expected_metrics.json"


def _flat(results: dict) -> dict:
    out = {}
    for task in ("demand", "supplier"):
        for split in ("val", "test"):
            for k, v in results[task][split].items():
                out[f"{task}.{split}.{k}"] = v
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--update", action="store_true")
    a = ap.parse_args()
    actual = _flat(json.loads(ACTUAL.read_text()))
    if a.update:
        EXPECTED.write_text(json.dumps(actual, indent=2, sort_keys=True))
        print(f"[reproduce] wrote {EXPECTED}")
        return 0
    if not EXPECTED.exists():
        print("[reproduce] no expected_metrics.json; run with --update first")
        return 2
    tol = load_params()["reproduce"]["rel_tolerance"]
    expected = json.loads(EXPECTED.read_text())
    bad = []
    for k, e in expected.items():
        v = actual.get(k)
        if v is None or abs(v - e) > tol * max(abs(e), 1e-9):
            bad.append((k, e, v))
    print(f"{'metric':32s} {'expected':>10s} {'actual':>10s}")
    for k, e in sorted(expected.items()):
        print(f"{k:32s} {e:10.4f} {actual.get(k, float('nan')):10.4f}")
    if bad:
        print(f"[reproduce] MISMATCH in {len(bad)} metrics (tol={tol})")
        return 1
    print(f"[reproduce] OK - all {len(expected)} metrics reproduced (rel tol {tol})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
