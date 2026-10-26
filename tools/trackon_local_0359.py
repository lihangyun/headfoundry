"""Load-only helpers: no unverified coordinate or stochastic-depth fallback."""
from pathlib import Path
import torch
from torch.nn.init import trunc_normal_


def indices_to_coords(*args, **kwargs):
    raise RuntimeError("coordinate convention not yet admitted; load-only stage")


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
