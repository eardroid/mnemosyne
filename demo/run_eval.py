"""run_eval.py - convenience runner for the evaluation harness.

Usage:  python demo/run_eval.py
(equivalent to `python -m mnemosyne.evaluation`)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mnemosyne.evaluation import evaluate, _print_report

try:
    from mnemosyne.heldout import TEST_SET
except ImportError:
    TEST_SET = None

if __name__ == "__main__":
    _print_report(evaluate(), "Dev set (20 tuning examples)")
    if TEST_SET is not None:
        print()
        _print_report(
            evaluate(dataset=[(t, l) for t, l, _ in TEST_SET]),
            "Frozen held-out set (100 examples, rules untouched)",
        )
