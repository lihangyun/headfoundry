"""Hash-locked public artifact acquisition/metadata only;no model forward or private data."""

import argparse
import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

from check_opend4rt_loader_0262 import ROOT, check_sources, peak_working_set, sha256_file

OUT = ROOT / "assets/private/opend4rt-checkpoint-0263"
FILE = OUT / "opend4rt.ckpt"


def memory_headroom():
    class Memory(ctypes.Structure):
        _fields_ = [("length", wintypes.DWORD), ("load", wintypes.DWORD)] + [
            (n, ctypes.c_ulonglong) for n in ["total", "available", "page_total", "page_available",
                                            "virtual_total", "virtual_available", "extended"]]
    status = Memory()
    status.length = ctypes.sizeof(status)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise ctypes.WinError()
    return {"available_ram_bytes": status.available, "process_commitable_bytes": status.page_available}


def checked_lock():
    lock = json.loads((ROOT / "examples/opend4rt-checkpoint-0263.asset-lock.json").read_text())
    if (lock.get("purpose") != "published_checkpoint_structural_conformance_only"
            or lock.get("source_license") != "Apache-2.0"
            or lock.get("checkpoint_license") != "Apache-2.0"
            or lock.get("deserialization") != {"weights_only": True, "mmap": False,
                                                "map_location": "meta", "strict": True,
                                                "metadata_mode": "FakeTensorMode"}
            or any(lock.get(k) is not False for k in ["forward_allowed", "human_material_allowed",
                                                      "training_allowed", "upload_allowed"])):
        raise ValueError("Missing rights or incompatible diagnostic scope")
    check_sources()
    return lock


def verify_file(lock, path=FILE):
    if path.is_symlink() or path.resolve().parent != OUT.resolve():
        raise ValueError("Unexpected artifact target")
    if path.stat().st_size != lock["checkpoint_bytes"]:
        raise ValueError("Wrong whole-file length")
    if sha256_file(path) != lock["checkpoint_sha256"]:
        raise ValueError("Wrong whole-file SHA256")


def download(lock):
    if FILE.exists():
        verify_file(lock)
        print("Existing exact artifact verified;no duplicate download")
        return
    if shutil.disk_usage(ROOT).free < 25_000_000_000:
        raise RuntimeError("Insufficient disk headroom")
    partial = OUT / "opend4rt.ckpt.part"
    command = ["curl.exe", "--fail", "--location", "--silent", "--show-error",
               "--connect-timeout", "30", "--max-time", "1790", "--retry", "2",
               "--retry-max-time", "1790", "--continue-at", "-", "--output", str(partial),
               "--write-out", '{"code":%{http_code},"bytes":%{size_download},"seconds":%{time_total}}',
               lock["checkpoint_url"]]
    with (OUT / "download-stats.json").open("w") as stdout, (OUT / "download-stderr.txt").open("w") as stderr:
        worker = subprocess.Popen(command, cwd=ROOT, stdout=stdout, stderr=stderr)
        (OUT / "download-handle.json").write_text(json.dumps({"parent_pid": os.getpid(), "worker_pid": worker.pid}))
        try:
            code = worker.wait(timeout=1800)
        except subprocess.TimeoutExpired:
            worker.kill()
            worker.wait()
            raise RuntimeError("Original download deadline exhausted")
    if code:
        raise RuntimeError(f"Fixed artifact download failed:{code}")
    verify_file(lock, partial)
    partial.rename(FILE)
    (OUT / "artifact-verification.json").write_text(json.dumps({
        "bytes": FILE.stat().st_size, "sha256": lock["checkpoint_sha256"], "whole_file_verified": True}))
    print("Exact published artifact length/SHA256 verified")


def fake_metadata(path):
    import torch
    from torch._subclasses.fake_tensor import FakeTensorMode
    # No full-file copy-on-write mapping/commit reservation,even for a training checkpoint.
    with FakeTensorMode():
        return torch.load(path, weights_only=True, mmap=False, map_location="meta")


def self_check(lock):
    import pickle
    import torch
    from unittest.mock import patch
    fixture = ROOT / "assets/private/opend4rt-loader-0262/fixture-good.pt"
    digest = sha256_file(fixture)
    ordinary = torch.load(fixture, weights_only=True, mmap=False)["model"]
    with patch.object(torch.UntypedStorage, "from_file", side_effect=AssertionError("File mapping forbidden")):
        fake = fake_metadata(fixture)["model"]
    if (ordinary.keys() != fake.keys() or not all(v.is_meta for v in fake.values())
            or any((v.shape, v.dtype, v.stride()) != (fake[k].shape, fake[k].dtype, fake[k].stride())
                   for k, v in ordinary.items())):
        raise ValueError("Metadata-only fixture mismatch")
    try:
        fake_metadata(fixture.with_name("fixture-unsupported.pt"))
    except pickle.UnpicklingError:
        pass
    else:
        raise AssertionError("Unsupported serialization accepted")
    if sha256_file(fixture) != digest:
        raise ValueError("Fixture changed")
    report = {"status": "TECHNICAL_CHECK_PASSED", "scope": "small_metadata_io_control_only",
              "torch_version": torch.__version__, "state_entries": len(fake),
              "all_meta": True, "file_mapping_forbidden_control_passed": True,
              "shape_dtype_stride_equal": True, "unsupported_serialization_rejected": True,
              "fixture_unchanged": True, "peak_working_set_bytes": peak_working_set()}
    (OUT / "self-check-report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report))


def inspect(lock):
    before = memory_headroom()
    if min(before.values()) < 2_000_000_000:
        raise RuntimeError("Insufficient metadata-inspection memory headroom")
    verify_file(lock)  # Before importing Torch or deserializing anything.
    source = check_sources()
    import torch
    import numpy as np
    import yaml
    if (torch.__version__ != source["runtime"]["torch"] or np.__version__ != source["runtime"]["numpy"]
            or yaml.__version__ != source["runtime"]["PyYAML"]):
        raise ValueError("Unexpected isolated runtime")
    sys.path.insert(0, str(ROOT / "assets/private/opend4rt-loader-0262/upstream"))
    from src.model.d4rt import D4RTModel
    torch.set_num_threads(8)
    torch.set_num_interop_threads(1)
    payload = fake_metadata(FILE)
    state = payload["model"]
    if not isinstance(state, dict) or not state:
        raise ValueError("Missing pure tensor model state")
    inventory = {}
    for name, value in state.items():
        if not isinstance(value, torch.Tensor) or not value.is_meta or value.dtype != torch.float32:
            raise ValueError("Unexpected model tensor type/device/dtype:" + name)
        inventory[name] = {"shape": list(value.shape), "dtype": str(value.dtype), "numel": value.numel()}
    config = yaml.safe_load((ROOT / "assets/private/opend4rt-loader-0262/model.yaml").read_text())["model"]
    if config["encoder"]["pretrained"]["enabled"] is not False:
        raise ValueError("Unapproved external initializer")
    with torch.device("meta"):
        model = D4RTModel(config)
    model.load_state_dict(state, strict=True, assign=True)
    count = sum(v.numel() for v in model.parameters())
    size = sum(v.numel() * v.element_size() for v in model.parameters())
    if (count != 1162433293 or size != 4649733172
            or not all(v.is_meta and v.dtype == torch.float32 for v in model.parameters())):
        raise ValueError("Unexpected full model structure")
    peak = peak_working_set()
    if peak >= 1_000_000_000:
        raise RuntimeError("Metadata-only process exceeded memory budget")
    (OUT / "tensor-inventory.json").write_text(json.dumps(inventory, indent=2))
    report = dict(status="TECHNICAL_CHECK_PASSED", scope="published_checkpoint_metadata_conformance_only",
                  checkpoint_sha256=lock["checkpoint_sha256"], whole_file_verified=True,
                  payload_categories={str(k): type(v).__name__ for k, v in payload.items()},
                  strict_model_state_entries=len(state), parameter_count=count, parameter_bytes=size,
                  all_model_parameters_meta=True, dtype="float32", resource_headroom_before=before,
                  metadata_mode="FakeTensorMode", full_file_mapping=False,
                  peak_working_set_bytes=peak, finite_parameter_values="UNVERIFIED",
                  materialized_model_resources="UNVERIFIED", known3d_accuracy="UNVERIFIED",
                  camera_status="UNVERIFIED", head_status="UNVERIFIED", human_material_read=False,
                  training=False, upload=False, forward_executed=False)
    (OUT / "report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["download", "inspect", "self-check"])
    action = parser.parse_args().action
    OUT.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    result = {"pid": os.getpid(), "action": action, "status": "RUNNING"}
    try:
        {"download": download, "inspect": inspect, "self-check": self_check}[action](checked_lock())
        result["status"] = "SUCCEEDED"
    except BaseException as error:
        result.update(status="FAILED", error_type=type(error).__name__, error=str(error))
        raise
    finally:
        result["seconds"] = time.perf_counter() - started
        (OUT / (action + "-process.json")).write_text(json.dumps(result, indent=2))
