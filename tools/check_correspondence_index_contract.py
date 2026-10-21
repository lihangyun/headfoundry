"""Deterministic index-identity witnesses, not a matcher or camera estimator."""
import json

import numpy as np


def selected_pairs(scores):
    """Compare aligned edge identities with same-ordinal row/column maxima."""
    scores = np.asarray(scores, float)
    if scores.shape != (81, 81) or not np.isfinite(scores).all():
        raise ValueError('Finite9x9-token score matrix required by this witness')
    ids = np.arange(81)
    x, y = ids % 9, ids // 9
    interior = (x >= 2) & (x < 7) & (y >= 2) & (y < 7)
    eligible = ((scores > .2) & (scores == scores.max(0, keepdims=True))
                & (scores == scores.max(1, keepdims=True))
                & interior[:, None] & interior[None, :])
    masked = np.where(eligible, scores, 0)
    row_valid, column_valid = masked.max(1) > 0, masked.max(0) > 0
    row_target, column_source = masked.argmax(1), masked.argmax(0)
    aligned = np.stack([ids[row_valid], row_target[row_valid]], axis=1)
    reference = np.argwhere(eligible)
    # The reported HF construction aligns two oppositely indexed maps by ordinal.
    common = row_valid & column_valid
    same_ordinal = np.stack([column_source[common], row_target[common]], axis=1)
    return aligned, reference, same_ordinal


def gather_window(grid, indices):
    """Select a fine cell, not a candidate-match row, after adding a batch axis."""
    grid, indices = np.asarray(grid), np.asarray(indices)
    if (grid.ndim != 4 or grid.shape[-1] != 2 or indices.shape != grid.shape[:2]
            or indices.dtype.kind not in 'iu' or (indices < 0).any()
            or (indices >= grid.shape[2]).any()):
        raise ValueError('Valid batch/match/window index required')
    index = np.repeat(indices[:, :, None, None], 2, axis=-1)
    return np.take_along_axis(grid, index, axis=2).squeeze(2)


def check():
    ids = [30, 31, 39]
    score = np.zeros((81, 81))
    score[ids, [31, 39, 30]] = [.9, .8, .7]
    aligned, reference, wrong = selected_pairs(score)
    if not np.array_equal(aligned, reference):
        raise ValueError('Aligned source/target identity lost')
    correct_set = {tuple(pair) for pair in reference}
    wrong_count = sum(tuple(pair) not in correct_set for pair in wrong)
    if wrong_count != 3:
        raise ValueError('Interior cycle did not expose same-ordinal defect')
    identity = np.zeros_like(score)
    identity[ids, ids] = [.9, .8, .7]
    a, b, c = selected_pairs(identity)
    if not np.array_equal(a, b) or not np.array_equal(b, c):
        raise ValueError('Identity control')
    if any(len(value) for value in selected_pairs(np.zeros_like(score))):
        raise ValueError('Empty input fabricated pairs')
    xx, yy = np.meshgrid(np.arange(8) - 3.5, np.arange(8) - 3.5)
    cells = np.stack([xx, yy], axis=-1).reshape(64, 2)
    grid = np.broadcast_to(cells, (2, 81, 64, 2))
    indices = ((np.arange(162) * 13 + 7) % 64).reshape(2, 81)
    result = gather_window(grid, indices)
    # Enumerated coordinate reference does not use a gather operation.
    expected = np.stack([indices % 8 - 3.5, indices // 8 - 3.5], axis=-1)
    if not np.array_equal(result, expected):
        raise ValueError('Window-axis gather differs from enumerated cells')
    # Exact torch.gather(axis1) semantics: non-gather fine dimension has index0.
    wrong_gather = grid[np.arange(2)[:, None], indices, np.zeros_like(indices)]
    wrong_fine = int(np.count_nonzero(np.any(wrong_gather != expected, axis=-1)))
    if wrong_fine == 0:
        raise ValueError('Wrong-axis witness did not fail')
    for bad in (-np.ones_like(indices), indices.astype(float), indices + 64):
        try:
            gather_window(grid, bad)
        except ValueError:
            continue
        raise ValueError('Invalid index accepted')
    return {'status': 'TECHNICAL_CHECK_PASSED', 'scope': 'Index contracts only',
        'aligned_pairs': aligned.tolist(), 'same_ordinal_pairs': wrong.tolist(),
        'same_ordinal_incorrect_pairs': wrong_count, 'fine_cells_checked': 162,
        'window_axis_max_error': float(np.abs(result - expected).max()),
        'match_axis_incorrect_cells': wrong_fine, 'identity_empty_invalid_controls': True,
        'physical_model_camera_head': 'UNVERIFIED', 'human_input': False}


if __name__ == '__main__':
    print(json.dumps(check(), indent=2))
