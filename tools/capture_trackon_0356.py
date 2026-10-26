"""Capture pinned, non-executed source evidence; never imports downloaded code."""
import ast
import hashlib
import json
import sys
from pathlib import Path
import urllib.request

REV = "7672a5e5432a20930d8a9fbba3340fff383138f7"
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets/private/trackon-source-0356"
PATHS = ["LICENSE", "config/test_dinov2.yaml", "model/trackon.py",
         "model/backbone.py", "model/modules.py", "model/prediction_head.py",
         "model/reranking.py", "model/trackon_predictor.py",
         "model/vit_adapter/dinov2_adapter/dinov2_adapter_modules.py",
         "model/vit_adapter/dinov2_adapter/dinov2_vit_adapter.py"]


def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": "HeadFoundry-source-audit"})
    with urllib.request.urlopen(request, timeout=20) as response:
        data = response.read(1_000_001)
    if len(data) > 1_000_000:
        raise ValueError("source size budget exceeded")
    return data


def main():
    offline = sys.argv[1:] == ["--offline"]
    if sys.argv[1:] not in ([], ["--offline"]):
        raise SystemExit("usage: capture_trackon_0356.py [--offline]")
    tree_path = OUT / "tree.json"
    tree_bytes = tree_path.read_bytes() if offline else fetch(f"https://api.github.com/repos/gorkaydemir/track_on/git/trees/{REV}?recursive=1")
    tree = json.loads(tree_bytes)
    assert tree["sha"] == REV and not tree["truncated"]
    entries = {item["path"]: item for item in tree["tree"]}
    records = []
    OUT.mkdir(parents=True, exist_ok=True)
    if not offline:
        tree_path.write_bytes(tree_bytes)
    for name in PATHS:
        target = OUT / (name + ".txt")  # Evidence only, never on Python import path.
        url = f"https://raw.githubusercontent.com/gorkaydemir/track_on/{REV}/{name}"
        data = target.read_bytes() if offline or target.exists() else fetch(url)
        git_hash = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        assert git_hash == entries[name]["sha"] and len(data) == entries[name]["size"], name
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            target.write_bytes(data)
        imports = []
        if name.endswith(".py"):
            for node in ast.walk(ast.parse(data)):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    imports.append(ast.unparse(node))
        records.append({"path": name, "url": url, "git_blob": git_hash,
                        "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
                        "imports": imports})
    report = {"status": "UNVERIFIED", "runtime_allowed": False,
              "revision": REV, "files": records,
              "excluded": ["utils/coord_utils.py", "evaluation/", "dataset/", "model/loss.py",
                           "utils/train_utils.py", "model/vit_adapter/dinov3_adapter/"]}
    (OUT / "capture.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
