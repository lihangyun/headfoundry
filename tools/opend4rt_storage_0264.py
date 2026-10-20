"""Lossless model-only storage packaging;no training or precision conversion."""

import hashlib
import json
from pathlib import Path
import struct
import sys
import zipfile

from check_opend4rt_loader_0262 import ROOT, check_sources, sha256_file
from inspect_opend4rt_checkpoint_0263 import fake_metadata


def pack(source, prefix, expected_sha):
    import numpy as np
    import torch
    source, prefix = Path(source), Path(prefix)
    if sha256_file(source) != expected_sha:
        raise ValueError("Original checkpoint digest mismatch")
    target, record_path = prefix.with_suffix(".bin"), prefix.with_suffix(".json")
    if target.exists() or record_path.exists():
        raise FileExistsError("Preserve first packaging attempt")
    state = fake_metadata(source)["model"]
    seen, rows, total = set(), {}, 0
    with zipfile.ZipFile(source) as archive, source.open("rb") as raw, target.open("xb") as output:
        byteorder = [n for n in archive.namelist() if n.endswith("/byteorder")]
        if len(byteorder) != 1 or archive.read(byteorder[0]) != b"little":
            raise ValueError("Explicit little-endian checkpoint required")
        by_offset = {}
        for info in archive.infolist():
            raw.seek(info.header_offset)
            header = raw.read(30)
            if header[:4] != b"PK\x03\x04":
                raise ValueError("Invalid ZIP local header")
            name_size, extra_size = struct.unpack_from("<HH", header, 26)
            by_offset[info.header_offset + 30 + name_size + extra_size] = info
        for name, tensor in state.items():
            if (not isinstance(tensor, torch.Tensor) or tensor.dtype != torch.float32
                    or not tensor.is_contiguous() or tensor.storage_offset() != 0 or tensor.numel() <= 0):
                raise ValueError("Unsupported model storage:" + name)
            storage = tensor.untyped_storage()
            offset, size = storage._checkpoint_offset, storage.nbytes()
            if offset in seen or size != tensor.numel() * 4:
                raise ValueError("Aliased/oversized model storage:" + name)
            seen.add(offset)
            info = by_offset[offset]
            if info.compress_type != zipfile.ZIP_STORED or info.file_size != size or "/data/" not in info.filename:
                raise ValueError("Unexpected storage ZIP member")
            digest, copied = hashlib.sha256(), 0
            with archive.open(info) as member:
                while chunk := member.read(1024 * 1024):
                    if not np.isfinite(np.frombuffer(chunk, dtype="<f4")).all():
                        raise ValueError("Nonfinite learned values:" + name)
                    digest.update(chunk)
                    output.write(chunk)
                    copied += len(chunk)
            if copied != size:
                raise ValueError("Incomplete storage copy")
            rows[name] = dict(shape=list(tensor.shape), stride=list(tensor.stride()), offset=total,
                              bytes=size, sha256=digest.hexdigest(), source_offset=offset)
            total += size
    if sha256_file(source) != expected_sha:
        raise ValueError("Original checkpoint changed")
    record = dict(source_sha256=expected_sha, source_license="Apache-2.0", dtype="float32",
                  bytes=total, tensors=rows, all_source_values_finite=True, flat_sha256=sha256_file(target))
    record_path.write_text(json.dumps(record, indent=2))
    return record


def verify_bound(model, record):
    for name, tensor in model.state_dict().items():
        row = record["tensors"][name]
        if tensor.dtype != __import__("torch").float32 or tensor.is_meta or not tensor.is_contiguous():
            raise ValueError("Unexpected bound tensor:" + name)
        digest = hashlib.sha256(memoryview(tensor.detach().numpy()).cast("B")).hexdigest()
        if digest != row["sha256"]:
            raise ValueError("Bound learned bytes changed:" + name)


def load_model(model, prefix):
    import torch
    from src.model.query_embedding import FourierFeatures
    prefix = Path(prefix)
    path = prefix.with_suffix(".bin")
    record = json.loads(prefix.with_suffix(".json").read_text())
    if (record["dtype"] != "float32" or record["source_license"] != "Apache-2.0"
            or path.stat().st_size != record["bytes"] or sha256_file(path) != record["flat_sha256"]):
        raise ValueError("Invalid packed model")
    storage = torch.UntypedStorage.from_file(str(path), shared=False, nbytes=record["bytes"])
    state = {}
    cursor = 0
    for name, row in record["tensors"].items():
        if row["offset"] != cursor or row["offset"] % 4:
            raise ValueError("Invalid packed tensor range")
        state[name] = torch.empty(0, dtype=torch.float32).set_(storage, cursor // 4, row["shape"], row["stride"])
        cursor += row["bytes"]
    if cursor != record["bytes"]:
        raise ValueError("Incomplete packed state")
    model.load_state_dict(state, strict=True, assign=True)
    if [n for n, t in model.named_buffers() if t.is_meta] != ["query_embedder.uv_encoder.frequencies"]:
        raise ValueError("Unexpected nonpersistent buffer")
    old = model.query_embedder.uv_encoder
    old.frequencies = FourierFeatures(old.input_dim, old.num_bands, old.include_input).frequencies
    if any(t.is_meta for t in model.parameters()) or any(t.is_meta for t in model.buffers()):
        raise ValueError("Unmaterialized model")
    if any(t.data_ptr() != state[n].data_ptr() for n, t in model.named_parameters()):
        raise ValueError("Assigned storage copied")
    verify_bound(model, record)
    return model.eval().requires_grad_(False), record


def self_check(prefix):
    import torch
    check_sources()
    sys.path.insert(0, str(ROOT / "assets/private/opend4rt-loader-0262/upstream"))
    from src.model.d4rt import D4RTModel
    config = {"input": {"clip_frames": 2, "channels": 3, "use_aspect_ratio_token": True},
              "encoder": {"hidden_dim": 16, "num_heads": 4, "num_layers": 2, "mlp_ratio": 2,
                          "patch_size_t_h_w": [1, 4, 4], "max_tokens": 32,
                          "attention_pattern": "interleaved_local_framewise_and_global",
                          "pretrained": {"enabled": False}},
              "decoder": {"hidden_dim": 16, "num_heads": 4, "num_layers": 2, "mlp_ratio": 2},
              "query_embedding": {"uv_num_bands": 8, "local_rgb_patch": {"enabled": True, "patch_size": 9}}}
    source = ROOT / "assets/private/opend4rt-loader-0262/fixture-good.pt"
    digest = sha256_file(source)
    record = pack(source, prefix, digest)
    ordinary = D4RTModel(config).eval()
    ordinary.load_state_dict(torch.load(source, weights_only=True, mmap=False)["model"], strict=True)
    with torch.device("meta"):
        model = D4RTModel(config)
    model, _ = load_model(model, prefix)
    for name, value in ordinary.state_dict().items():
        if not torch.equal(value.view(torch.uint8), model.state_dict()[name].view(torch.uint8)):
            raise ValueError("Tiny learned bytes differ")
    video = torch.arange(384, dtype=torch.float32).reshape(1, 2, 3, 8, 8) / 383
    ids = torch.arange(9)
    query = dict(u=(ids[None].float()+1)/10, v=(9-ids[None].float())/10,
                 t_src=(ids%2)[None], t_tgt=((ids+1)%2)[None], t_cam=((ids//2)%2)[None])
    with torch.inference_mode():
        a, b = ordinary({"video": video, "query": query}), model({"video": video, "query": query})
        memory = model.encode_video(video)
        parts = [model.decode_queries(video, {k: v[:, i:i+3] for k, v in query.items()}, memory) for i in range(0,9,3)]
    for key in a:
        torch.testing.assert_close(a[key], b[key], atol=1e-6, rtol=1e-6)
        torch.testing.assert_close(b[key], torch.cat([x[key] for x in parts], 1), atol=1e-6, rtol=1e-6)
        if not torch.isfinite(b[key]).all():
            raise ValueError("Nonfinite tiny output")
    verify_bound(model, record)
    if sha256_file(source) != digest:
        raise ValueError("Tiny source changed")
    return {"status": "TECHNICAL_CHECK_PASSED", "scope": "lossless_tiny_pack_control_only",
            "state_entries": len(record["tensors"]), "all_learned_bytes_equal": True,
            "source_fixture_unchanged": True, "output_and_chunk_tolerance": 1e-6}
