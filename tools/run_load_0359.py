"""Bounded load-only admission, never invokes inference."""
import json
import os
from pathlib import Path
import sys
from bounded_process import run

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets/private/trackon-load-0359"


def main():
    stage = sys.argv[1]
    python = ROOT / ".venv-trackon0357/Scripts/python.exe"
    if stage == "install":
        command = ["C:/Users/lihan/.local/bin/uv.exe", "--no-cache", "pip", "install", "--python", str(python),
                   "transformers==4.56.1", "safetensors==0.6.2", "numpy==2.2.6"]
        seconds, memory = 600, 4 * 1024**3
    elif stage == "check":
        command = [str(python), str(ROOT / "tools/check_trackon_load_0359.py")]
        seconds, memory = 120, 2 * 1024**3
    else:
        raise ValueError("unknown stage")
    receipt = OUT / (stage + "-worker.json")
    if receipt.exists():
        raise RuntimeError("inspect existing receipt before replay")
    env = os.environ.copy()
    env.update(PYTHONDONTWRITEBYTECODE="1", HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1", OMP_NUM_THREADS="4")
    result = run(command, ROOT, env, OUT / (stage + ".log"), receipt, seconds, memory)
    print(json.dumps(result))
    if result["status"] != "TECHNICAL_CHECK_PASSED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
