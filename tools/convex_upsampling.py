"""Independent NumPy oracle for 8x, 3x3 convex upsampling; not a model adapter.

Algorithm contract reviewed against aharley/alltracker e7553135 (MIT).
This checker does not certify CUDA/network equivalence or physical precision.
"""
import json
import time

import numpy as np


def convex_upsample(values, logits, *, chunked=True):
    """Two channels, zero-padded 3x3 support; batch1 chunks retain every value."""
    values, logits = np.asarray(values), np.asarray(logits)
    if values.ndim != 4 or values.shape[1] != 2 or min(values.shape) < 1:
        raise ValueError('expected nonempty N,2,H,W')
    n, _, h, w = values.shape
    if logits.shape != (n, 576, h, w):
        raise ValueError('expected N,576,H,W logits')
    if values.dtype not in (np.float32, np.float64) or logits.dtype != values.dtype:
        raise ValueError('matching float32/float64 required')
    if not np.isfinite(values).all() or not np.isfinite(logits).all():
        raise ValueError('nonfinite input')
    result = np.empty((n, 2, h*8, w*8), dtype=values.dtype)
    # ponytail: fixed batch1 bounds product storage; this is not a GPU allocator bound.
    step = 1 if chunked else n
    for start in range(0, n, step):
        stop = min(start+step, n)
        mask = logits[start:stop].reshape(stop-start, 1, 9, 8, 8, h, w)
        weights = np.exp(mask-mask.max(axis=2, keepdims=True))
        weights /= weights.sum(axis=2, keepdims=True)
        padded = np.pad(values[start:stop]*8, ((0, 0), (0, 0), (1, 1), (1, 1)))
        neighbors = np.stack([padded[:, :, dy:dy+h, dx:dx+w]
                              for dy in range(3) for dx in range(3)], axis=2)
        combined = (weights*neighbors[:, :, :, None, None]).sum(axis=2)
        result[start:stop] = combined.transpose(0, 1, 4, 2, 5, 3).reshape(
            stop-start, 2, h*8, w*8)
    return result


def scalar_oracle(values, logits):
    """Direct per-output indexing, float64 accumulation, no unfold/transpose."""
    n, _, h, w = values.shape
    out = np.zeros((n, 2, h*8, w*8), dtype=np.float64)
    for b in range(n):
        for y in range(h*8):
            for x in range(w*8):
                iy, sy = divmod(y, 8)
                ix, sx = divmod(x, 8)
                a = logits[b, np.arange(9)*64+sy*8+sx, iy, ix].astype(np.float64)
                weights = np.exp(a-a.max())
                weights /= weights.sum()
                for k in range(9):
                    dy, dx = divmod(k, 3)
                    py, px = iy+dy-1, ix+dx-1
                    if 0 <= py < h and 0 <= px < w:
                        out[b, :, y, x] += weights[k]*8*values[b, :, py, px]
    return out


def audit():
    started = time.monotonic()
    rng = np.random.default_rng(293)
    rows = []
    for n in (1, 3, 16):
        raw = rng.uniform(-2, 2, (n, 2, 14, 22)).astype(np.float32)
        mask = rng.uniform(-4, 4, (n, 576, 14, 22)).astype(np.float32)
        for strided in (False, True):
            v, m = raw[:, :, ::2, ::2], mask[:, :, ::2, ::2]
            if not strided:
                v, m = v.copy(), m.copy()
            full, chunk = convex_upsample(v, m, chunked=False), convex_upsample(v, m)
            if chunk.shape != (n, 2, 56, 88) or not np.isfinite(chunk).all():
                raise ValueError('invalid output')
            if not np.array_equal(full, chunk):
                raise ValueError('batch partition differs')
            rows.append({'batch': n, 'strided': strided, 'values': chunk.size,
                         'max_delta': float(np.abs(full-chunk).max())})
    # Asymmetry in batch, channels, neighbors and subpixels exposes axis mistakes.
    v = np.arange(24, dtype=np.float32).reshape(2, 2, 2, 3)/32-0.25
    m = rng.uniform(-2, 2, (2, 576, 2, 3)).astype(np.float32)
    errors = []
    for label, a in [('asymmetric', m), ('uniform', np.zeros_like(m))]:
        actual, expected = convex_upsample(v, a), scalar_oracle(v, a)
        delta = float(np.abs(actual-expected).max())
        if delta > 1e-5:
            raise ValueError('independent pixel oracle failed')
        errors.append({'fixture': label, 'values': actual.size, 'max_delta_px': delta})
    invalid = [(v[:, :1], m), (v[:0], m[:0]), (v, m[:, :-1]),
               (v.astype(np.int32), m), (v, m.astype(np.float64)),
               (v*np.nan, m), (v, m+np.inf)]
    for a, b in invalid:
        try:
            convex_upsample(a, b)
        except ValueError:
            continue
        raise ValueError('invalid input accepted')
    return {'status': 'TECHNICAL_CHECK_PASSED', 'scope': 'NumPy algebra/index only',
            'network_physical_quality': 'UNVERIFIED', 'batch_controls': rows,
            'independent_oracle': errors, 'rejected_invalid_inputs': len(invalid),
            'native_product_bytes': 16*2*9*8*8*160*96*4,
            'chunk_product_bytes': 2*9*8*8*160*96*4,
            'seconds': time.monotonic()-started}


if __name__ == '__main__':
    print(json.dumps(audit(), indent=2))
