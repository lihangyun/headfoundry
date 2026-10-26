"""Local helpers; coordinate math independently specified in0360."""
from pathlib import Path
import torch
from torch.nn.init import trunc_normal_


def indices_to_coords(indices, size, stride):
    """Row-major feature-cell index to its center in input pixel-edge units.

    Independent arithmetic: cell(column,row) covers [column*s,(column+1)*s]
    by [row*s,(row+1)*s]. Return its midpoint as (x,y), preserving prefix shape.
    This is not a copy of the excluded vendor coordinate utility.
    """
    height, width = size
    if any(type(v) is not int or v <= 0 for v in (height, width, stride)):
        raise ValueError("positive integer geometry required")
    if height % stride or width % stride:
        raise ValueError("feature grid must tile input exactly")
    if indices.dtype not in (torch.int32, torch.int64):
        raise ValueError("integer cell indices required")
    columns, rows = width // stride, height // stride
    if torch.any(indices < 0) or torch.any(indices >= columns * rows):
        raise ValueError("cell index outside grid")
    column = indices.remainder(columns)
    row = torch.div(indices, columns, rounding_mode="floor")
    return (torch.stack((column, row), dim=-1).to(torch.float32) + .5) * stride


class DropPath(torch.nn.Module):
    def __init__(self, *args, **kwargs):
        raise RuntimeError("nonzero stochastic depth outside pinned small-model config")


def load_backbone():
    from transformers import Dinov2Config, Dinov2Model
    from safetensors.torch import load_file
    from assets_trackon_0358 import OUT, verify_config
    verify_config()
    config = Dinov2Config.from_json_file(str(OUT / "config.json"))
    assert config.drop_path_rate == 0 and config.hidden_size == 384
    model = Dinov2Model(config)
    state = load_file(str(OUT / "model.safetensors"))
    model.load_state_dict(state, strict=True)
    return model
