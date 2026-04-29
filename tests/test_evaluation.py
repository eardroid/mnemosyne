"""Tests for the evaluation harness (runs offline, no API needed)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mnemosyne.evaluation import evaluate, DATASET


def test_evaluation_runs_and_is_consistent():
    r = evaluate()

    assert r["tp"] + r["fp"] + r["tn"] + r["fn"] == r["total"] == len(DATASET)

    for key in ("precision", "recall", "f1", "accuracy"):
        assert 0.0 <= r[key] <= 1.0


    assert r["accuracy"] >= 0.5


def test_obvious_attack_is_caught():
    r = evaluate()


    assert r["recall"] >= 0.5
    assert r["precision"] == 1.0
