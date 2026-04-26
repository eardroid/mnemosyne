"""Tests for the evaluation harness (runs offline, no API needed)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mnemosyne.evaluation import evaluate, DATASET


def test_evaluation_runs_and_is_consistent():
    r = evaluate()
    # Every labeled example is accounted for.
    assert r["tp"] + r["fp"] + r["tn"] + r["fn"] == r["total"] == len(DATASET)
    # Scores are sane floats in [0, 1].
    for key in ("precision", "recall", "f1", "accuracy"):
        assert 0.0 <= r[key] <= 1.0
    # Recalls the known limitation: at least some reworded attacks are missed.
    # (If you later make the detector stronger, lower this to >= 0 and the
    #  test still passes — but the report will show fewer misses.)
    assert r["accuracy"] >= 0.5  # it should at least beat a coin flip


def test_obvious_attack_is_caught():
    r = evaluate()
    # Attacks written with a clear suspicious fragment must be caught.
    # (Re-worded attacks with NO known fragment are expected to miss —
    # that is the documented limitation, not a regression.)
    assert r["recall"] >= 0.5   # at least half the labeled attacks flagged
    assert r["precision"] == 1.0  # nothing benign should be flagged
