"""ONE command to reproduce everything:  python -m src.pipeline.run_all

generate raw data -> validate -> features + leak-free splits ->
baselines + primary models in MLflow -> register champions ->
verify metrics against reports/expected_metrics.json
"""
from __future__ import annotations

import subprocess
import sys

STEPS = [
    ("generate raw data", ["-m", "src.pipeline.generate_data"]),
    ("validate raw data", ["-m", "src.pipeline.validate"]),
    ("features + splits", ["-m", "src.pipeline.prepare"]),
    ("train + track + register", ["-m", "src.pipeline.train"]),
    ("verify reproduced metrics", ["-m", "src.pipeline.reproduce"]),
]


def main() -> int:
    for title, args in STEPS:
        print(f"\n=== {title} ===", flush=True)
        rc = subprocess.call([sys.executable, *args])
        if rc != 0:
            print(f"!!! step '{title}' failed (exit {rc})")
            return rc
    print("\nPipeline reproduced successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
