"""run_eval.py - convenience runner for the evaluation harness.

Usage:  python demo/run_eval.py
(equivalent to `python -m mnemosyne.evaluation`)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mnemosyne.evaluation import evaluate, _print_report

if __name__ == "__main__":
    _print_report(evaluate())
