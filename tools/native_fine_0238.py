"""Auditable rows around pinned XFeat's native learned refinement, no truth input."""
import numpy as np


def unique_coordinates(points):
    points = np.asarray(points)
    if points.ndim != 2 or points.shape[1:] != (2,) or not np.isfinite(points).all():
        raise ValueError('Finite Nx2 coordinates required')
    _, inverse, count = np.unique(points, axis=0, return_inverse=True, return_counts=True)
    return count[inverse] == 1


def refine_native(extractor, first, second):
    """First is target, second fixed reference; native features are never sparse IDs.

    Calls the upstream public refinement. A second fine-logit evaluation solely
    exposes the native confidence row mask which that public API omits. No new
    decoding, temperature, offset or threshold is introduced.
    """
    import torch
    for item in (first, second):
        for key, last in (('keypoints', 2), ('descriptors', 64)):
            value = item[key]
            if value.ndim != 3 or value.shape[0] != 1 or value.shape[2] != last or not torch.isfinite(value).all():
                raise ValueError('One finite native dense batch required')
        if (item['scales'].shape != item['keypoints'].shape[:2]
                or item['descriptors'].shape[:2] != item['keypoints'].shape[:2]
                or not torch.isfinite(item['scales']).all() or (item['scales'] <= 0).any()):
            raise ValueError('Matching finite native feature scales required')
    if min(first['keypoints'].shape[1], second['keypoints'].shape[1]) == 0:
        return {'source': np.empty((0, 2)), 'raw': np.empty((0, 2)), 'refined': np.empty((0, 2)),
            'matches': np.empty((0, 2), np.int64), 'confidence': np.empty(0),
            'native_keep': np.zeros(0, bool), 'identity_keep': np.zeros(0, bool)}
    frozen = [{k: item[k].clone() for k in ('keypoints', 'descriptors', 'scales')} for item in (first, second)]
    with torch.inference_mode():
        matches = extractor.batch_match(first['descriptors'], second['descriptors'])
        a, b = matches[0]
        raw, source = first['keypoints'][0, a].clone(), second['keypoints'][0, b].clone()
        if not len(a):
            confidence = torch.empty(0, device=raw.device)
            keep = torch.zeros(0, dtype=torch.bool, device=raw.device)
            refined = raw.clone()
        else:
            logits = extractor.net.fine_matcher(torch.cat([first['descriptors'][0, a], second['descriptors'][0, b]], dim=-1))
            if logits.shape != (len(a), 64) or not torch.isfinite(logits).all():
                raise ValueError('Finite native8x8 fine logits required')
            confidence = torch.softmax(logits * 3, dim=-1).max(dim=-1)[0]
            keep = confidence > .25
            native = extractor.refine_matches(first, second, matches, batch_idx=0)
            if native.shape != (int(keep.sum()), 4) or not torch.equal(native[:, 2:], source[keep]):
                raise ValueError('Native refinement row order or fixed reference anchor changed')
            refined = raw.clone()
            refined[keep] = native[:, :2]
        for item, snapshot in zip((first, second), frozen):
            if any(not torch.equal(item[k], snapshot[k]) for k in snapshot):
                raise ValueError('Native matching mutated input features')
    result = {key: value.detach().cpu().numpy().copy() for key, value in
        (('source', source), ('raw', raw), ('refined', refined), ('confidence', confidence), ('native_keep', keep))}
    result['matches'] = torch.stack([a, b], dim=-1).cpu().numpy().copy()
    result['identity_keep'] = unique_coordinates(result['source']) & unique_coordinates(result['raw'])
    return result
