"""Owned numerical controls; not geometric or patient evidence."""
import ast
import hashlib
import importlib.metadata
import importlib.util
import json
import math
from pathlib import Path
import socket
import torch

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets/private/trackon-software-0357"


def denied(*args, **kwargs):
    raise RuntimeError("network forbidden during operator controls")


def scalar_oracle(value, shapes, locations, weights):
    """Explicit four-neighbor bilinear sums, no grid_sample/vectorized reshape."""
    batch, queries, heads, levels, points, _ = locations.shape
    channels = value.shape[-1]
    result = torch.zeros(batch, queries, heads * channels, dtype=value.dtype)
    for b in range(batch):
        for q in range(queries):
            for head in range(heads):
                start = 0
                for level, (height, width) in enumerate(shapes.tolist()):
                    for point in range(points):
                        x, y = locations[b, q, head, level, point].tolist()
                        x, y = x * width - .5, y * height - .5
                        ix, iy = math.floor(x), math.floor(y)
                        for row in (iy, iy + 1):
                            for col in (ix, ix + 1):
                                if 0 <= row < height and 0 <= col < width:
                                    factor = (1 - abs(x - col)) * (1 - abs(y - row))
                                    for c in range(channels):
                                        result[b, q, head * channels + c] += (
                                            value[b, start + row * width + col, head, c]
                                            * weights[b, q, head, level, point] * factor)
                    start += height * width
    return result


def main():
    socket.socket.connect = denied
    socket.create_connection = denied
    torch.set_num_threads(4)
    torch.manual_seed(357)
    source = OUT / "hf_deformable.py"
    spec = importlib.util.spec_from_file_location("hf_deformable", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    original = ast.parse((OUT / "mmcv-source.txt").read_text())
    prepared = ast.parse(source.read_text())
    name = "multi_scale_deformable_attn_pytorch"
    nodes = [next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
             for tree in (original, prepared)]
    assert ast.dump(nodes[0]) == ast.dump(nodes[1]), "reference function changed"
    function = getattr(module, name)
    shapes = torch.tensor([[2, 3], [1, 2]])
    value = torch.randn(2, 8, 2, 3, dtype=torch.float64)
    locations = torch.rand(2, 3, 2, 2, 4, 2, dtype=torch.float64) * 2 - .5
    weights = torch.rand(2, 3, 2, 2, 4, dtype=torch.float64)
    expected = scalar_oracle(value, shapes, locations, weights)
    actual = function(value, shapes, locations, weights)
    error64 = float((actual - expected).abs().max())
    assert error64 < 1e-12
    error32 = float((function(value.float(), shapes, locations.float(), weights.float()).double() - expected).abs().max())
    assert error32 < 1e-5  # Numerical oracle tolerance, not any reconstruction gate.
    # Center of a 2x2 field -> average; extreme out-of-bounds -> zero.
    field = torch.tensor([1., 2., 3., 4.]).reshape(1, 4, 1, 1)
    coords = torch.tensor([.5, .5, -2., -2.]).reshape(1, 2, 1, 1, 1, 2)
    result = function(field, torch.tensor([[2, 2]]), coords, torch.ones(1, 2, 1, 1, 1))
    assert torch.equal(result.flatten(), torch.tensor([2.5, 0.]))
    layer = module.MultiScaleDeformableAttention(embed_dims=4, num_heads=1,
                  num_levels=2, num_points=2, dropout=0, batch_first=True).eval()
    required = {f"{prefix}.{suffix}" for prefix in (
        "sampling_offsets", "attention_weights", "value_proj", "output_proj")
        for suffix in ("weight", "bias")}
    assert set(layer.state_dict()) == required
    with torch.no_grad():
        layer.sampling_offsets.weight.zero_()
        layer.sampling_offsets.bias.zero_()
        for proj in (layer.value_proj, layer.output_proj):
            proj.weight.copy_(torch.eye(4))
            proj.bias.zero_()
        query = torch.arange(12, dtype=torch.float32).reshape(1, 3, 4)
        values = torch.full((1, 8, 4), 4.)
        args = dict(value=values, reference_points=torch.full((1, 3, 2, 2), .5),
                    spatial_shapes=shapes, level_start_index=torch.tensor([0, 6]))
        reference = layer(query, **args)
        assert torch.equal(reference, query + 4)
        assert torch.equal(layer(query, key_padding_mask=torch.ones(1, 8, dtype=torch.bool), **args), query)
        args["reference_points"] = torch.full((1, 3, 2, 4), .5)
        assert torch.equal(layer(query, **args), reference)
        layer.batch_first = False
        args["value"] = values.transpose(0, 1)
        assert torch.equal(layer(query.transpose(0, 1), **args).transpose(0, 1), reference)
    report = dict(status="TECHNICAL_CHECK_PASSED", scope="owned operator semantics only",
                  float64_max_error=error64, float32_max_error=error32,
                  generated_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                  packages=sorted((d.metadata["Name"], d.version) for d in importlib.metadata.distributions()),
                  model_inference="NOT_RUN", medical_accuracy="UNVERIFIED")
    (OUT / "controls.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
