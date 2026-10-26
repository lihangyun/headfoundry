"""Bounded isolated packaging/operator stages; never handles human inputs."""
import json
import os
from pathlib import Path
import subprocess
import sys
from bounded_process import run

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets/private/trackon-software-0357"
PYTHON = ROOT / ".venv-trackon0357/Scripts/python.exe"
UV = "C:/Users/lihan/.local/bin/uv.exe"


def main():
    stage = sys.argv[1]
    env = os.environ.copy()
    env.update(UV_CACHE_DIR=str(OUT / "cache"), PYTHONDONTWRITEBYTECODE="1",
               HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1", OMP_NUM_THREADS="4")
    if stage == "install":
        if not PYTHON.exists():
            subprocess.run([UV, "--no-cache", "venv", "--python", str(ROOT / ".venv/Scripts/python.exe"),
                            str(PYTHON.parents[1])], check=True, timeout=30, env=env)
        command = [UV, "--no-cache", "pip", "install", "--python", str(PYTHON),
                   "--index-url", "https://download.pytorch.org/whl/cpu", "torch==2.8.0+cpu"]
        seconds, memory = 600, 4 * 1024**3
    elif stage == "check":
        command = [str(PYTHON), str(ROOT / "tools/check_operator_0357.py")]
        seconds, memory = 120, 2 * 1024**3
    else:
        raise ValueError("unknown stage")
    receipt = OUT / (stage + "-worker.json")
    if receipt.exists():
        raise RuntimeError("existing stage receipt: inspect it before any replay")
    result = run(command, ROOT, env, OUT / (stage + ".log"), receipt, seconds, memory)
    print(json.dumps(result, indent=2))
    if result["status"] != "TECHNICAL_CHECK_PASSED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
