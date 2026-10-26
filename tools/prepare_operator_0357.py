"""Explicitly extract MMCV's permissive CPU reference, not a fake mmcv package."""
import ast
import hashlib
import json
from pathlib import Path
from capture_trackon_0356 import fetch

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets/private/trackon-software-0357"
URLS = {
    "mmcv-LICENSE": "https://raw.githubusercontent.com/open-mmlab/mmcv/v2.2.0/LICENSE",
    "mmcv-source.txt": "https://raw.githubusercontent.com/open-mmlab/mmcv/v2.2.0/mmcv/ops/multi_scale_deform_attn.py",
    "adapter-LICENSE": "https://raw.githubusercontent.com/czczup/ViT-Adapter/fd64a5190f9f4530e8e5961cc87b2a3ad591190b/LICENSE.md",
    "torch-LICENSE": "https://raw.githubusercontent.com/pytorch/pytorch/v2.8.0/LICENSE",
}
HASHES = {
    "mmcv-LICENSE": "866d999d3ca92d2c5dc9b0afc941c5fac6529e2d180fc638274f91f7fce161d7",
    "mmcv-source.txt": "b281995a765c245b182d9cad33781cd5f3dd1650e05967b7c8272982981fd9c3",
    "adapter-LICENSE": "975bf0101f2ebeed2ff7c96438080f6df0cfaf4d17c456f64ddcf2d9fe6db56c",
    "torch-LICENSE": "a8a2c6b67cf8a597ffaa5c82380a6bd1b82629c0417e00673d8013d662eb500a",
}


def prepare():
    OUT.mkdir(parents=True, exist_ok=True)
    records = []
    for name, url in URLS.items():
        path = OUT / name
        data = path.read_bytes() if path.exists() else fetch(url)
        if hashlib.sha256(data).hexdigest() != HASHES[name]:
            raise ValueError("source drift: " + name)
        if not path.exists():
            path.write_bytes(data)
        records.append(dict(name=name, url=url, bytes=len(data), sha256=hashlib.sha256(data).hexdigest()))
    for name in ("mmcv-LICENSE", "adapter-LICENSE"):
        if "Apache License" not in (OUT / name).read_text():
            raise ValueError("missing expected license")
    tree = ast.parse((OUT / "mmcv-source.txt").read_text())
    selected = [n for n in tree.body if isinstance(n, (ast.ClassDef, ast.FunctionDef))
                and n.name in ("multi_scale_deformable_attn_pytorch", "MultiScaleDeformableAttention")]
    assert len(selected) == 2
    cls = next(n for n in selected if isinstance(n, ast.ClassDef))
    cls.decorator_list = []
    cls.bases = [ast.parse("nn.Module", mode="eval").body]
    for method in cls.body:
        if not isinstance(method, ast.FunctionDef):
            continue
        method.decorator_list = []
        if method.name == "__init__":
            calls = [n for n in ast.walk(method) if isinstance(n, ast.Call)
                     and ast.unparse(n.func) == "super().__init__"]
            assert len(calls) == 1
            calls[0].args = []
        if method.name == "forward":
            branches = [n for n in method.body if isinstance(n, ast.If)
                        and "IS_CUDA_AVAILABLE" in ast.unparse(n.test)]
            assert len(branches) == 1
            branch = branches[0]
            i = method.body.index(branch)
            method.body[i:i + 1] = branch.orelse
    header = '''# Copyright (c) OpenMMLab. All rights reserved.
# Derived from MMCV v2.2.0; Apache-2.0, see adjacent mmcv-LICENSE.
# HeadFoundry changes: explicit CPU reference, nn.Module base, local init helpers.
from __future__ import annotations
import math
import warnings
import torch
from torch import nn
from torch.nn import functional as F

def constant_init(module, val, bias=0.):
    nn.init.constant_(module.weight, val)
    if module.bias is not None:
        nn.init.constant_(module.bias, bias)

def xavier_init(module, distribution="uniform", bias=0.):
    if distribution != "uniform":
        raise ValueError("only selected upstream uniform initializer supported")
    nn.init.xavier_uniform_(module.weight)
    if module.bias is not None:
        nn.init.constant_(module.bias, bias)

'''
    code = header + "\n\n".join(ast.unparse(n) for n in selected) + "\n"
    compile(code, "hf_deformable.py", "exec")  # Syntax only; never execute here.
    assert "ext_module" not in code and "import mmcv" not in code
    (OUT / "hf_deformable.py").write_text(code, encoding="utf-8", newline="\n")
    report = dict(status="UNVERIFIED", model_runtime_allowed=False, files=records,
                  generated_sha256=hashlib.sha256(code.encode()).hexdigest())
    (OUT / "source-record.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    prepare()
