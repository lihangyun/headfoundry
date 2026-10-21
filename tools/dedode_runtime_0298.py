"""Bounded independent inference glue; original MIT model modules stay unedited.

DeDoDe core/models: Copyright 2023 Johan Edstedt, MIT (staged source/LICENSE).
No upstream pose, augmentation, training or GPL-attributed helper is imported.
These elementary tensor/grid/matching operations are not anatomical validation.
"""
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT/'assets/private/sparse-runtime-0298'
LOCK = json.loads((ROOT/'examples/dedode-0298-lock.json').read_text())
os.environ.setdefault('USERNAME', Path(os.environ['USERPROFILE']).name)
os.environ['TORCHINDUCTOR_CACHE_DIR'] = str(DEST/'inductor-cache')
os.environ['CUDA_CACHE_PATH'] = str(DEST/'cuda-cache')
os.environ['TORCH_HOME'] = str(DEST/'torch-cache')
import torch
import torch.nn.functional as F


def get_best_device(verbose=False):
    # No automatic CPU/MPS fallback for the registered CUDA recipe.
    return torch.device('cuda:0')


def sample_keypoints(scoremap, num_samples=8192, device=None, use_nms=True,
                     sample_topk=False, return_scoremap=False, sharpen=False,
                     upsample=False, increase_coverage=False, remove_borders=False):
    if use_nms or not sample_topk or sharpen or upsample or not increase_coverage or remove_borders:
        raise ValueError('only registered deterministic coverage/top-k inference supported')
    if scoremap.ndim != 3 or scoremap.dtype != torch.float32 or not torch.isfinite(scoremap).all():
        raise ValueError('finite FP32 B,H,W probability map required')
    b, h, w = scoremap.shape
    if min(b, h, w) < 1 or not 0 < num_samples <= h*w or (scoremap < 0).any() or (scoremap.sum((1, 2)) <= 0).any():
        raise ValueError('invalid probability support')
    if device is not None and torch.device(device).type != scoremap.device.type:
        raise ValueError('sampling device differs')
    axis = torch.linspace(-2, 2, 51, device=scoremap.device)
    kernel = torch.exp(-axis**2)
    density = F.conv2d((scoremap[:, None]+1e-6)*10000,
                       kernel.reshape(1, 1, 1, 51), padding=(0, 25))
    density = F.conv2d(density, kernel.reshape(1, 1, 51, 1), padding=(25, 0))[:, 0]
    ranked = scoremap*(density+1e-8)**(-.5)
    indices = ranked.flatten(1).topk(num_samples, dim=1).indices
    xs = torch.linspace(-1+1/w, 1-1/w, w, device=scoremap.device)
    ys = torch.linspace(-1+1/h, 1-1/h, h, device=scoremap.device)
    locations = torch.stack((xs[indices % w], ys[indices // w]), dim=-1)
    return (locations, ranked.flatten(1).gather(1, indices)) if return_scoremap else locations


def to_pixel_coords(points, height, width):
    """Publisher pixel-edge convention, kept internal; not OpenCV indices."""
    size = points.new_tensor([width, height])
    return size*(points+1)/2


def to_normalized_coords(points, height, width):
    return 2*points/points.new_tensor([width, height])-1


def cv_pixels(points, height, width):
    return to_pixel_coords(points, height, width)-.5


def normalized_from_cv(points, height, width):
    return to_normalized_coords(points+.5, height, width)


def dual_softmax_matcher(desc_A, desc_B, inv_temperature=1, normalize=False):
    if desc_A.ndim == 2:
        desc_A, desc_B = desc_A[None], desc_B[None]
    if desc_A.ndim != 3 or desc_B.ndim != 3 or desc_A.shape[0] != desc_B.shape[0] or desc_A.shape[2] != desc_B.shape[2]:
        raise ValueError('matching descriptor batches/channels required')
    if any(d.dtype != torch.float32 or not torch.isfinite(d).all() for d in (desc_A, desc_B)):
        raise ValueError('finite FP32 descriptors required')
    if normalize:
        a, b = desc_A.norm(dim=-1, keepdim=True), desc_B.norm(dim=-1, keepdim=True)
        if (a <= 0).any() or (b <= 0).any():
            raise ValueError('zero descriptor norm')
        desc_A, desc_B = desc_A/a, desc_B/b
    scores = torch.einsum('bnc,bmc->bnm', desc_A, desc_B)*inv_temperature
    return scores.softmax(-2)*scores.softmax(-1)


def match_indices(probabilities, threshold=.1):
    """Retain all mutual ties; caller must not count them as one-to-one support."""
    chosen = ((probabilities == probabilities.amax(-1, keepdim=True)) &
              (probabilities == probabilities.amax(-2, keepdim=True)) &
              (probabilities > threshold))
    pairs = chosen.nonzero()
    b, n, m = probabilities.shape
    ambiguous = False
    if len(pairs):
        left = pairs[:, 0]*n+pairs[:, 1]
        right = pairs[:, 0]*m+pairs[:, 2]
        ambiguous = bool((torch.bincount(left) > 1).any() or (torch.bincount(right) > 1).any())
    return pairs, ambiguous


def normalize_rgb(image):
    if image.ndim != 4 or image.shape[1] != 3 or image.dtype != torch.float32:
        raise ValueError('native float32 B,RGB,H,W input required')
    if not torch.isfinite(image).all() or image.min() < 0 or image.max() > 255:
        raise ValueError('RGB input outside0..255')
    mean = image.new_tensor([.485, .456, .406])[None, :, None, None]
    std = image.new_tensor([.229, .224, .225])[None, :, None, None]
    return (image/255-mean)/std


def core_modules():
    if 'DeDoDe' in sys.modules:
        raise RuntimeError('unexpected pre-existing DeDoDe package')
    # Namespace directories intentionally contain no upstream package initializer.
    sys.path.insert(0, str(DEST/'source'))
    sys.modules['DeDoDe.utils'] = sys.modules[__name__]
    from DeDoDe.model_zoo import dedode_models
    from DeDoDe.detectors import dedode_detector
    return dedode_models, dedode_detector
