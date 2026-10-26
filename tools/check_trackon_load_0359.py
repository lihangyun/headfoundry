"""Strict full-state loading only. All model forward calls remain prohibited."""
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import socket
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets/private/trackon-load-0359"
sys.path.insert(0, str(OUT))
sys.path.insert(0, str(ROOT / "tools"))
os.environ.update(HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1", HF_HUB_DISABLE_TELEMETRY="1")


def denied(*args, **kwargs):
    raise RuntimeError("network forbidden during strict loading")


def main():
    socket.socket.connect = denied
    socket.create_connection = denied
    import torch
    from safetensors.torch import load_file
    from assets_trackon_0358 import verify, verify_config
    from model.trackon import Track_On2
    torch.set_num_threads(4)
    verify_config()
    assets = ROOT / "assets/private/trackon-assets-0358"
    for asset in json.loads((ROOT / "examples/trackon2-0356.preflight-lock.json").read_text())["assets"]:
        verify(assets / asset["filename"], asset["expected_bytes"], asset["publisher_sha256"])
    args = SimpleNamespace(input_size=[384,512], M=24, M_i=72, D=256, K=16,
        decoder_layer_num=3, predicton_head_layer_num=3, rerank_layer_num=3,
        vit_backbone="dinov2_s", vit_upsample_factor=1, grad_checkpoint=True, delta_v=.8)
    # Read exact numeric field spelling from frozen config without a YAML dependency.
    for line in (ROOT / "assets/private/trackon-source-0356/config/test_dinov2.yaml.txt").read_text().splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            if value.strip().isdigit():
                setattr(args, key.strip(), int(value.strip()))
    model = Track_On2(args).eval()
    raw = torch.load(assets / "trackon2_dinov2_checkpoint.pt", map_location="cpu", weights_only=True)
    for key in ("state_dict", "model", "model_state", "ema_state_dict"):
        if key in raw and isinstance(raw[key], dict):
            raw = raw[key]
            break
    state = {k.removeprefix("module."): v for k, v in raw.items()}
    assert len(state) == len(raw), "prefix collision"
    backbone = load_file(str(assets / "model.safetensors"))
    prefix = "backbone.vit_encoder.dinov2."
    for key, value in backbone.items():
        full = prefix + key
        if full in state:
            assert torch.equal(state[full], value), "conflicting backbone tensor"
        state[full] = value
    expected = model.state_dict()
    missing = sorted(set(expected) - set(state))
    extra = sorted(set(state) - set(expected))
    shape_errors = [k for k in set(expected) & set(state) if expected[k].shape != state[k].shape]
    report = dict(status="UNVERIFIED", missing=missing, extra=extra, shape_errors=shape_errors,
                  expected_keys=len(expected), supplied_keys=len(state), model_forward="NOT_RUN")
    (OUT / "load-result.json").write_text(json.dumps(report, indent=2))
    assert not missing and not extra and not shape_errors
    model.load_state_dict(state, strict=True)
    assert all(torch.equal(v, state[k]) for k, v in model.state_dict().items())
    report.update(status="TECHNICAL_CHECK_PASSED", all_loaded_tensors_exact=True,
                  packages=sorted((d.metadata["Name"], d.version) for d in importlib.metadata.distributions()))
    (OUT / "load-result.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
