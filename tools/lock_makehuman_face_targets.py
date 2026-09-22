"""Create a fail-closed lock for reviewed CC0 MakeHuman face target folders."""
import argparse
import json
import subprocess
from pathlib import Path

from headfoundry.manifest import sha256_file


FOLDERS = ("asym", "cheek", "chin", "ears", "eyebrows", "eyes",
           "forehead", "head", "neck", "nose", "mouth")
REVISION = "a8bc2d54ff0ac92e78ff71431b1023eda42bf482"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkout", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    revision = subprocess.run(
        ["git", "-C", str(args.checkout), "rev-parse", "HEAD"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    if revision != REVISION:
        raise ValueError("unexpected MakeHuman revision")
    target_root = args.checkout / "makehuman/data/targets"
    files = sorted(path for folder in FOLDERS for path in (target_root / folder).rglob("*.target"))
    if len(files) < 300:
        raise ValueError("incomplete reviewed face target checkout")
    hashes = {}
    for path in files:
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:8])
        if "explicitly released as CC0" not in head:
            raise ValueError("missing explicit CC0 header: " + str(path))
        hashes[path.relative_to(target_root).as_posix()] = sha256_file(path)
    lock = {
        "asset_id": "makehuman-full-face-targets",
        "source": "https://github.com/makehumancommunity/makehuman",
        "revision": REVISION,
        "source_directory": "makehuman/data/targets",
        "license_id": "CC0-1.0",
        "license_evidence": "LICENSE.md section C and explicit CC0 header in every locked target",
        "base_asset_lock": "makehuman-base-asset-lock.json",
        "scope": "Reviewed face/head graphical displacement targets only; no application code or trained model",
        "folders": list(FOLDERS),
        "sha256": hashes,
    }
    args.output.write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"revision": revision, "target_count": len(files), "output": str(args.output)}))


if __name__ == "__main__":
    main()
