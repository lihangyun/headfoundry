"""Deterministic IO checks,not released-model inference or reconstruction."""

import copy
import ctypes
from ctypes import wintypes
import datetime
import json
from pathlib import Path
import pickle
import sys
import time

if not __debug__:
    raise RuntimeError("Run this diagnostic without -O;checks must remain enabled.")

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets/private/opend4rt-loader-0262"
sys.path.insert(0, str(ROOT / "src"))
from headfoundry.manifest import sha256_file


def peak_working_set():
    class Counters(ctypes.Structure):
        _fields_ = [("cb", wintypes.DWORD), ("faults", wintypes.DWORD)] + [
            (n, ctypes.c_size_t) for n in ["peak", "working", "paged_peak", "paged",
                                          "nonpaged_peak", "nonpaged", "pagefile", "pagefile_peak"]]
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    psapi = ctypes.WinDLL("psapi", use_last_error=True)
    psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
    psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
    counters = Counters()
    counters.cb = ctypes.sizeof(counters)
    if not psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(), ctypes.byref(counters), counters.cb):
        raise ctypes.WinError(ctypes.get_last_error())
    return counters.peak


def check_sources():
    lock = json.loads((ROOT / "examples/opend4rt-loader-0262.source-lock.json").read_text())
    if (lock.get("source_license") != "Apache-2.0"
            or lock.get("published_checkpoint_license") != "Apache-2.0"
            or lock.get("full_checkpoint_execution_allowed_by_this_lock") is not False
            or lock.get("human_material_allowed") is not False
            or lock.get("training_allowed") is not False):
        raise ValueError("Missing or unsupported rights/scope declaration")
    for name, digest in lock["source_files"].items():
        if sha256_file(OUT / "upstream" / name) != digest:
            raise ValueError("Changed reviewed source: " + name)
    if sha256_file(OUT / "model.yaml") != lock["config_sha256"]:
        raise ValueError("Changed pinned architecture config")
    return lock


def run():
    started = time.perf_counter()
    lock = check_sources()
    import torch
    import numpy as np
    import yaml
    if (torch.__version__ != lock["runtime"]["torch"]
            or np.__version__ != lock["runtime"]["numpy"]
            or yaml.__version__ != lock["runtime"]["PyYAML"]):
        raise ValueError("Unexpected isolated runtime version")
    torch.set_num_threads(8)
    torch.set_num_interop_threads(1)
    sys.path.insert(0, str(OUT / "upstream"))
    from src.model.d4rt import D4RTModel
    from src.model.query_embedding import FourierFeatures

    config = {"input": {"clip_frames": 2, "channels": 3, "use_aspect_ratio_token": True},
              "encoder": {"hidden_dim": 16, "num_heads": 4, "num_layers": 2,
                          "mlp_ratio": 2, "patch_size_t_h_w": [1, 4, 4], "max_tokens": 32,
                          "attention_pattern": "interleaved_local_framewise_and_global",
                          "pretrained": {"enabled": False}},
              "decoder": {"hidden_dim": 16, "num_heads": 4, "num_layers": 2, "mlp_ratio": 2},
              "query_embedding": {"uv_num_bands": 8,
                                  "local_rgb_patch": {"enabled": True, "patch_size": 9}}}

    def factory():
        return D4RTModel(config)

    def low_peak_load(path, expected_sha):
        if path.resolve().parent != OUT.resolve() or path.is_symlink():
            raise ValueError("Only local synthetic fixtures are allowed in0262")
        if sha256_file(path) != expected_sha:
            raise ValueError("Checkpoint checksum mismatch")
        payload = torch.load(path, map_location="cpu", weights_only=True, mmap=True)
        state = payload["model"]
        if not isinstance(state, dict) or not all(isinstance(v, torch.Tensor) for v in state.values()):
            raise ValueError("Expected a pure tensor model state")
        for name, value in state.items():
            if value.dtype != torch.float32:
                raise ValueError("Model dtype mismatch: " + name)
            if not torch.isfinite(value).all():
                raise ValueError("Nonfinite model tensor: " + name)
        with torch.device("meta"):
            model = factory()
        model.load_state_dict(state, strict=True, assign=True)
        meta_buffers = [n for n, v in model.named_buffers() if v.is_meta]
        if meta_buffers != ["query_embedder.uv_encoder.frequencies"]:
            raise ValueError("Unexpected unresolved meta buffers")
        old = model.query_embedder.uv_encoder
        old.frequencies = FourierFeatures(old.input_dim, old.num_bands, old.include_input).frequencies
        if any(v.is_meta for v in model.parameters()) or any(v.is_meta for v in model.buffers()):
            raise ValueError("Unmaterialized model state")
        for name, value in model.named_parameters():
            if value.data_ptr() != state[name].data_ptr():
                raise ValueError("Assigned storage was copied")
        return model.eval()

    torch.manual_seed(262)
    original = factory().eval()
    original_state = {n: v.detach().clone() for n, v in original.state_dict().items()}
    fixture = OUT / "fixture-good.pt"
    torch.save({"model": original_state, "optimizer": {"state": {"test": {
        "exp_avg": torch.zeros(2), "exp_avg_sq": torch.zeros(2)}}},
                "scheduler": {"last_epoch": 0}, "scaler": {}, "test_only": True}, fixture)
    digest = sha256_file(fixture)
    ordinary = factory().eval()
    ordinary.load_state_dict(torch.load(fixture, map_location="cpu", weights_only=True)["model"], strict=True)
    loaded = low_peak_load(fixture, digest)
    for name, value in loaded.state_dict().items():
        assert torch.equal(value, original_state[name]), name
    for (_, a), (_, b) in zip(ordinary.named_buffers(), loaded.named_buffers()):
        assert torch.equal(a, b)

    video = torch.arange(2 * 3 * 8 * 8, dtype=torch.float32).reshape(1, 2, 3, 8, 8) / 383
    index = torch.arange(9)
    queries = {"u": (index.float()[None] + 1) / 10,
               "v": (9 - index.float()[None]) / 10,
               "t_src": (index % 2)[None], "t_tgt": ((index + 1) % 2)[None],
               "t_cam": ((index // 2) % 2)[None]}
    with torch.inference_mode():
        baseline = ordinary({"video": video, "query": queries})
        prediction = loaded({"video": video, "query": queries})
        memory = loaded.encode_video(video)
        chunks = [loaded.decode_queries(video, {k: v[:, i:i+3] for k, v in queries.items()}, memory)
                  for i in range(0, 9, 3)]
    output_error = max(float((baseline[k] - prediction[k]).abs().max()) for k in baseline)
    chunk_error = max(float((prediction[k] - torch.cat([c[k] for c in chunks], 1)).abs().max())
                      for k in prediction)
    for key in baseline:
        torch.testing.assert_close(prediction[key], baseline[key], rtol=1e-6, atol=1e-6)
        torch.testing.assert_close(torch.cat([c[key] for c in chunks], 1), prediction[key], rtol=1e-6, atol=1e-6)
    assert sha256_file(fixture) == digest
    assert all(torch.equal(v, original_state[n]) for n, v in loaded.state_dict().items())

    rejected = []
    key = next(iter(original_state))
    for kind in ["missing", "extra", "shape", "dtype", "nonfinite", "checksum", "unsupported"]:
        state = {n: v.clone() for n, v in original_state.items()}
        if kind == "missing": del state[key]
        if kind == "extra": state["unexpected"] = torch.zeros(1)
        if kind == "shape": state[key] = state[key].flatten()[:-1]
        if kind == "dtype": state[key] = state[key].double()
        if kind == "nonfinite": state[key].flatten()[0] = float("nan")
        payload = {"model": state}
        if kind == "unsupported": payload["unsupported"] = datetime.datetime(2026, 1, 1)
        path = OUT / ("fixture-" + kind + ".pt")
        torch.save(payload, path)
        try:
            low_peak_load(path, "0" * 64 if kind == "checksum" else sha256_file(path))
        except (RuntimeError, ValueError, KeyError, pickle.UnpicklingError):
            rejected.append(kind)
        else:
            raise AssertionError("Negative fixture accepted: " + kind)

    full_config = yaml.safe_load((OUT / "model.yaml").read_text())["model"]
    assert full_config["encoder"]["pretrained"]["enabled"] is False
    with torch.device("meta"):
        full = D4RTModel(full_config)
    parameter_count = sum(v.numel() for v in full.parameters())
    parameter_bytes = sum(v.numel() * v.element_size() for v in full.parameters())
    assert parameter_count == 1162433293 and parameter_bytes == 4649733172
    assert all(v.is_meta for v in full.parameters())
    assert all(v.dtype == torch.float32 for v in full.parameters())
    peak = peak_working_set()
    elapsed = time.perf_counter() - started
    assert peak < 2_000_000_000 and elapsed < 120
    report = dict(status="TECHNICAL_CHECK_PASSED", scope="synthetic_loader_and_structural_invariants_only",
                  source_commit=lock["source_commit"], runtime=lock["runtime"],
                  fixture_sha256=digest, learned_tensors_bit_equal=True, assigned_storages_alias=True,
                  nonpersistent_buffers_equal=True, output_max_abs_error=output_error,
                  chunk_max_abs_error=chunk_error, rejected_cases=rejected,
                  full_meta_parameters=parameter_count, full_meta_parameter_bytes=parameter_bytes,
                  full_parameters_remained_meta=True, peak_working_set_bytes=peak, seconds=elapsed,
                  checkpoint_downloaded=False, human_material_read=False, training=False, upload=False,
                  real_checkpoint_compatibility="UNVERIFIED", camera_status="UNVERIFIED", head_status="UNVERIFIED")
    (OUT / "report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report))


if __name__ == "__main__":
    run()
