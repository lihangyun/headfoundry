"""Prepare load-only adaptation from verified source; no model import here."""
import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets/private/trackon-source-0356"
OUT = ROOT / "assets/private/trackon-load-0359"


class Adapt(ast.NodeTransformer):
    def visit_Import(self, node):
        if any(a.name.startswith("torchvision") for a in node.names):
            return None
        return node

    def visit_ImportFrom(self, node):
        replacements = {"mmcv.ops": "hf_deformable", "utils.coord_utils": "hf_local",
                        "timm.layers": "hf_local"}
        if node.module in replacements:
            node.module = replacements[node.module]
        if node.module == "transformers":
            return ast.parse("from hf_local import load_backbone").body[0]
        return node

    def visit_Call(self, node):
        self.generic_visit(node)
        if ast.unparse(node.func) == "AutoModel.from_pretrained":
            return ast.copy_location(ast.Call(func=ast.Name(id="load_backbone", ctx=ast.Load()), args=[], keywords=[]), node)
        return node

    def visit_If(self, node):
        if ast.unparse(node.test) == "model_name == 'dinov3'":
            return ast.parse("assert args.vit_backbone == 'dinov2_s'").body + [self.visit(n) for n in node.orelse]
        return self.generic_visit(node)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    capture = json.loads((SOURCE / "capture.json").read_text())
    prepared = []
    for record in capture["files"]:
        name = record["path"]
        if not name.endswith(".py") or name.endswith("trackon_predictor.py"):
            continue
        data = (SOURCE / (name + ".txt")).read_bytes()
        assert hashlib.sha256(data).hexdigest() == record["sha256"]
        tree = ast.parse(data)
        loaded = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}
        assert "torchvision" not in loaded  # T may denote tensor sequence length, not transform alias.
        assert not any(isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id == "T" for n in ast.walk(tree))
        tree = ast.fix_missing_locations(Adapt().visit(tree))
        code = "# Adapted from Track-On2 pinned source; see LICENSE and adapter-LICENSE.\n" + ast.unparse(tree) + "\n"
        if "vit_adapter" in name:
            code = "# Copyright (c) Shanghai AI Lab. All rights reserved.\n" + code
        compile(code, name, "exec")
        target = OUT / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(code, encoding="utf8", newline="\n")
        prepared.append(dict(path=name, source_sha256=record["sha256"], adapted_sha256=hashlib.sha256(code.encode()).hexdigest()))
    for name, path in {"LICENSE": SOURCE / "LICENSE.txt",
                       "adapter-LICENSE": ROOT / "assets/private/trackon-software-0357/adapter-LICENSE",
                       "mmcv-LICENSE": ROOT / "assets/private/trackon-software-0357/mmcv-LICENSE",
                       "hf_local.py": ROOT / "tools/trackon_local_0359.py",
                       "hf_deformable.py": ROOT / "assets/private/trackon-software-0357/hf_deformable.py"}.items():
        (OUT / name).write_bytes(path.read_bytes())
    (OUT / "prepared.json").write_text(json.dumps(dict(status="UNVERIFIED", files=prepared), indent=2))
    print("Prepared", len(prepared), "load-only source files")


if __name__ == "__main__":
    main()
