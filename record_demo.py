"""Generate an asciicast v2 (.cast) file by running the demo and capturing output."""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

CAST_FILE = Path("mnemosyne_demo.cast")
ASSETS_DIR = Path("assets")
ASSETS_DIR.mkdir(exist_ok=True)


def generate_cast():
    header = {
        "version": 2,
        "width": 100,
        "height": 40,
        "timestamp": int(time.time()),
        "env": {"SHELL": "powershell", "TERM": "xterm-256color"},
        "title": "Mnemosyne Demo — Memory Poisoning Defence",
    }

    print("Recording demo to mnemosyne_demo.cast ...")

    proc = subprocess.Popen(
        [sys.executable, "demo/run_demo.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=os.getcwd(),
        env={**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUNBUFFERED": "1"},
    )

    start = time.time()
    lines = []

    for raw_line in iter(proc.stdout.readline, b""):
        elapsed = round(time.time() - start, 6)
        text = raw_line.decode("utf-8", errors="replace")
        lines.append([elapsed, "o", text])

    proc.wait()

    with open(CAST_FILE, "w", encoding="utf-8") as f:
        f.write(json.dumps(header) + "\n")
        for entry in lines:
            f.write(json.dumps(entry) + "\n")

    print(f"Saved {CAST_FILE} ({len(lines)} frames)")
    print(f"\nTo create a GIF, download agg from:")
    print(f"  https://github.com/asciinema/agg/releases")
    print(f"Then run:")
    print(f"  agg mnemosyne_demo.cast assets/demo.gif")


if __name__ == "__main__":
    generate_cast()
