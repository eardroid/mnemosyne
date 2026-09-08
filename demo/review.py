"""review.py - human-in-the-loop update path for the detector.

The rules don't learn on their own (deliberate: a learner fed by memory
writes could be poisoned into accepting poison). Improvement happens here:
a person looks at what the guard recently saw, confirms real attacks, and
those confirmed texts accumulate in reviewed_attacks.json.

That file is NOT loaded automatically. Promoting a reviewed text into
semantic.py BAD_EXAMPLES (or a phrase into detector.py) is a deliberate
manual edit, so every behavior change is a conscious diff, never silent.

Usage:  python demo/review.py [--db mnemosyne.db] [--n 20]
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mnemosyne.ledger import Ledger

REVIEWED_PATH = Path(__file__).resolve().parent.parent / "mnemosyne" / "reviewed_attacks.json"


def main() -> None:
    args = parse_args()
    ledger = Ledger(args.db)
    rows = ledger.get_recent(args.n)
    if not rows:
        print("ledger is empty, nothing to review.")
        return

    print("recent writes (id, status, trust, score, text):")
    for r in reversed(rows):
        print(f"  [{r['id']}] {r['status']:<7} trust={r['trust_level']:<6} "
              f"score={r['confidence']:.2f}  {r['content'][:70]}")

    raw = input("ids of CONFIRMED attacks (comma separated, blank = none): ").strip()
    if not raw:
        print("nothing marked.")
        return

    wanted = {int(x) for x in raw.replace(" ", "").split(",") if x}
    by_id = {r["id"]: r for r in rows}
    confirmed = [by_id[i]["content"] for i in sorted(wanted) if i in by_id]

    reviewed = []
    if REVIEWED_PATH.exists():
        reviewed = json.loads(REVIEWED_PATH.read_text())
    have = {r["text"] for r in reviewed}
    added = 0
    for text in confirmed:
        if text not in have:
            reviewed.append({
                "text": text,
                "reviewed_at": datetime.now(timezone.utc).isoformat(),
            })
            have.add(text)
            added += 1
    REVIEWED_PATH.write_text(json.dumps(reviewed, indent=2) + "\n")
    print(f"added {added}, {len(reviewed)} total in {REVIEWED_PATH.name}.")
    print("promote them into semantic.py BAD_EXAMPLES by hand if you want them live.")


def parse_args():
    p = argparse.ArgumentParser(description="review recent guard decisions")
    p.add_argument("--db", default="mnemosyne.db")
    p.add_argument("--n", type=int, default=20)
    return p.parse_args()


if __name__ == "__main__":
    main()
