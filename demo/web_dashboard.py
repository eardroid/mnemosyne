"""web_dashboard.py — a small Flask app to click through the guard.

Run it with:   python demo/web_dashboard.py
Then open:       http://localhost:5000

This is a teaching UI. The memory store behind it is the SQLite-backed
SqliteMemory from mnemosyne.guard, so memories survive a restart and it
all works offline with no API keys. The detector is the offline rule
scorer. There is an OPTIONAL local-LLM (Ollama) "secondary defense" you
can enable by running Ollama with a model pulled — it can only TIGHTEN a
borderline stored write into a block, and it is ignored on any error.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from flask import Flask, jsonify, render_template, request

from mnemosyne.guard import MemoryGuard, SimpleMemory
from mnemosyne.sqlite_memory import SqliteMemory

app = Flask(
    __name__,
    template_folder=str(Path(__file__).parent / "templates"),
    static_folder=str(Path(__file__).parent / "static"),
)


guard = MemoryGuard(memory=SqliteMemory())

SEED_MEMORIES = [
    "TechSupplies Inc legitimate account is ACC-1234-LEGIT",
    "All vendor payments need two approvals",
    "Finance contact is finance@company.com",
]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/stats")
def api_stats():
    return jsonify(guard.ledger.get_stats())


@app.route("/api/recent")
def api_recent():
    return jsonify(guard.ledger.get_recent(20))


@app.route("/api/memories")
def api_memories():
    return jsonify(guard.memory.get_all())


@app.route("/api/setup", methods=["POST"])
def api_setup():
    guard.memory.clear()
    results = [guard.safe_add(m, source="internal") for m in SEED_MEMORIES]
    return jsonify(_summarize(results))


@app.route("/api/inject", methods=["POST"])
def api_inject():
    data = request.get_json(force=True, silent=True) or {}
    content = (data.get("content") or "").strip()
    source = data.get("source", "email")
    if not content:
        return jsonify({"error": "content is required"}), 400
    result = guard.safe_add(content, source=source)
    return jsonify(_detail(result))


@app.route("/api/ask", methods=["POST"])
def api_ask():
    data = request.get_json(force=True, silent=True) or {}
    question = (data.get("question") or "").strip()
    if not question:
        return jsonify({"error": "question is required"}), 400
    hits = guard.memory.search(question)
    context = " ".join(h["memory"] for h in hits)
    return jsonify({
        "question": question,
        "memories_used": len(hits),
        "context": context or "No relevant memories found.",
    })


@app.route("/api/reset", methods=["POST"])
def api_reset():
    guard.memory.clear()
    return jsonify({"cleared": True, "reloaded": 0})


def _summarize(results: list[dict]) -> list[dict]:
    return [{"status": r["status"], "content": r["content"]} for r in results]


def _detail(result: dict) -> dict:
    """Shape a guard result for the frontend."""
    out = {
        "status": result["status"],
        "trust": result["trust"],
        "score": result["score"],
        "attack_type": result["attack_type"],
        "matched_labels": [m["label"] for m in result["matched"]],
        "block_reason": result["block_reason"],
        "content": result["content"],
    }
    if result.get("llm_note"):
        out["llm_note"] = result["llm_note"]
    return out


if __name__ == "__main__":
    print("\n  Mnemosyne web demo")
    print("  ------------------")
    print("  Open http://localhost:5000\n")
    app.run(host="127.0.0.1", port=5000, debug=False, threaded=True)
