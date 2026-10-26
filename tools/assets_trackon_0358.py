"""Pinned public asset capture and safe tensor inventory; no model execution."""
import hashlib
import json
import os
from pathlib import Path
import struct
import sys
import urllib.request
from bounded_process import run

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets/private/trackon-assets-0358"
LOCK = ROOT / "examples/trackon2-0356.preflight-lock.json"


def verify(path, size, digest):
    if path.stat().st_size != size:
        raise ValueError("wrong size: " + path.name)
    with path.open("rb") as stream:
        actual = hashlib.file_digest(stream, "sha256").hexdigest()
    if actual != digest:
        raise ValueError("hash mismatch: " + path.name)


def download():
    for asset in json.loads(LOCK.read_text())["assets"]:
        target = OUT / asset["filename"]
        if not target.exists():
            url = f'https://huggingface.co/{asset["repository"]}/resolve/{asset["revision"]}/{asset["filename"]}'
            partial = target.with_suffix(target.suffix + ".partial")
            if partial.exists():
                raise RuntimeError("partial download requires inspection, not silent replay")
            count = 0
            with urllib.request.urlopen(url, timeout=30) as response, partial.open("xb") as stream:
                while chunk := response.read(1024 * 1024):
                    count += len(chunk)
                    if count > asset["expected_bytes"]:
                        raise ValueError("download size exceeded")
                    stream.write(chunk)
            verify(partial, asset["expected_bytes"], asset["publisher_sha256"])
            partial.rename(target)
        verify(target, asset["expected_bytes"], asset["publisher_sha256"])
        print("Verified", target.name, flush=True)
    config = OUT / "config.json"
    if not config.exists():
        url = "https://huggingface.co/facebook/dinov2-small/resolve/ed25f3a31f01632728cabb09d1542f84ab7b0056/config.json"
        with urllib.request.urlopen(url, timeout=30) as response:
            data = response.read(10000)
        digest = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        if digest != "5664b325e6258d3960fad8c4c1cff958f3cc2272":
            raise ValueError("config drift")
        config.write_bytes(data)


def inspect():
    import torch
    for asset in json.loads(LOCK.read_text())["assets"]:
        verify(OUT / asset["filename"], asset["expected_bytes"], asset["publisher_sha256"])
    raw = torch.load(OUT / "trackon2_dinov2_checkpoint.pt", map_location="cpu", weights_only=True)
    if not isinstance(raw, dict):
        raise TypeError("checkpoint is not a dictionary")
    state = raw
    for key in ("state_dict", "model", "model_state", "ema_state_dict"):
        if key in raw and isinstance(raw[key], dict):
            state = raw[key]
            break
    if not state or any(not isinstance(k, str) or not isinstance(v, torch.Tensor) for k, v in state.items()):
        raise TypeError("non-tensor state")
    tensors = {}
    for name, tensor in state.items():
        if not torch.isfinite(tensor).all():
            raise ValueError("nonfinite tensor: " + name)
        tensors[name] = dict(shape=list(tensor.shape), dtype=str(tensor.dtype), numel=tensor.numel())
    path = OUT / "model.safetensors"
    with path.open("rb") as stream:
        header_size = struct.unpack("<Q", stream.read(8))[0]
        if header_size > 1_000_000:
            raise ValueError("oversize header")
        header = json.loads(stream.read(header_size))
    ranges = []
    for name, info in header.items():
        if name == "__metadata__":
            continue
        count = 1
        for dim in info["shape"]:
            if not isinstance(dim, int) or dim < 0:
                raise ValueError("bad tensor shape")
            count *= dim
        start, end = info["data_offsets"]
        if info["dtype"] != "F32" or end - start != count * 4:
            raise ValueError("unexpected backbone dtype/offsets")
        ranges.append((start, end))
    cursor = 0
    for start, end in sorted(ranges):
        if start != cursor:
            raise ValueError("gap/overlap in tensor bytes")
        cursor = end
    if cursor + header_size + 8 != path.stat().st_size:
        raise ValueError("incomplete payload")
    report = dict(status="TECHNICAL_CHECK_PASSED", scope="asset identity and tensor inventory",
                  tracker_tensors=tensors, backbone_header=header,
                  full_model_state_coverage="UNVERIFIED", model_forward="NOT_RUN")
    (OUT / "tensor-inventory.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(dict(tracker_tensors=len(tensors), tracker_numel=sum(x["numel"] for x in tensors.values()),
                         backbone_tensors=len(ranges), backbone_numel=cursor // 4)))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    stage = sys.argv[1]
    if stage == "download-worker":
        download()
    elif stage == "inspect-worker":
        inspect()
    elif stage in ("download", "inspect"):
        receipt = OUT / (stage + "-worker.json")
        if receipt.exists():
            raise RuntimeError("inspect existing stage receipt before replay")
        env = os.environ.copy()
        env.update(PYTHONDONTWRITEBYTECODE="1", OMP_NUM_THREADS="4", HF_HUB_OFFLINE="1")
        python = ROOT / (".venv/Scripts/python.exe" if stage == "download" else ".venv-trackon0357/Scripts/python.exe")
        result = run([str(python), __file__, stage + "-worker"], ROOT, env,
                     OUT / (stage + ".log"), receipt, 600 if stage == "download" else 120,
                     (1 if stage == "download" else 2) * 1024**3)
        print(json.dumps(result))
        if result["status"] != "TECHNICAL_CHECK_PASSED":
            raise SystemExit(1)
    else:
        raise ValueError("unknown stage")


if __name__ == "__main__":
    main()
