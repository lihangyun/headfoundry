"""All-row RGB gradient ridge,not an absolute color crossing or material anchor."""
import numpy as np
from scipy.ndimage import gaussian_filter1d


def gradient_profile(rgb, box, sigma=1.):
    rgb = np.asarray(rgb, float)
    if (rgb.ndim != 3 or rgb.shape[2] != 3 or not np.isfinite(rgb).all()
            or sigma not in (.75, 1., 1.25)):
        raise ValueError('Finite RGB and one declared measurement scale required')
    x0, y0, x1, y1 = box
    if not (0 <= x0 < x1 <= rgb.shape[1] and 0 <= y0 < y1 <= rgb.shape[0]) or x1-x0 < 5:
        raise ValueError('Unclipped image ROI required')
    strength = np.linalg.norm(gaussian_filter1d(rgb[y0:y1, x0:x1], sigma, axis=1, order=1, mode='nearest'), axis=2)
    peaks = np.zeros_like(strength, bool)
    peaks[:, 1:-1] = ((strength[:, 1:-1] >= strength[:, :-2])
        & (strength[:, 1:-1] >= strength[:, 2:]) & (strength[:, 1:-1] >= 2))
    if not peaks.any(axis=1).all():
        raise ValueError('Missing measurable gradient row')
    unary = -np.log(np.maximum(strength, 1e-30) / np.maximum(strength.max(axis=1, keepdims=True), 1e-30))
    unary[~peaks] = np.inf
    cost = unary[0].copy()
    previous = np.empty_like(strength, dtype=int)
    delta = np.arange(-8, 9)
    for row in range(1, len(strength)):
        windows = np.lib.stride_tricks.sliding_window_view(np.pad(cost, 8, constant_values=np.inf), 17)
        transitions = windows + .01 * delta[None, :] ** 2
        chosen = np.argmin(transitions, axis=1)
        previous[row] = np.arange(len(cost)) + delta[chosen]
        cost = unary[row] + np.min(transitions, axis=1)
    if not np.isfinite(cost).any():
        raise ValueError('No continuous all-row gradient ridge')
    path = np.empty(len(strength), int)
    path[-1] = int(cost.argmin())
    for row in range(len(strength)-1, 0, -1):
        path[row-1] = previous[row, path[row]]
    if (path <= 0).any() or (path >= strength.shape[1]-1).any():
        raise ValueError('Gradient ridge clipped by search ROI')
    rows = np.arange(len(path))
    left, center, right = strength[rows, path-1], strength[rows, path], strength[rows, path+1]
    curvature = left - 2*center + right
    offset = np.zeros(len(path))
    sharp = curvature < -1e-12
    offset[sharp] = .5*(left[sharp]-right[sharp])/curvature[sharp]
    if (abs(offset) > .5 + 1e-8).any():
        raise ValueError('Selected gradient is not an interior local maximum')
    return np.c_[x0 + path + .5 + offset, y0 + rows + .5], strength[rows, path]


def known_boundary_fixture(direction):
    if direction not in (-1, 1):
        raise ValueError('Signed fixture orientation required')
    h, w = 213, 190
    y = np.arange(h) + .5
    edge = (115 + .08*y + 26*np.exp(-((y-62)/18)**2)
        - 9*np.exp(-((y-92)/8)**2) + 8*np.exp(-((y-115)/9)**2)
        + 6*np.exp(-((y-136)/11)**2) - 22/(1+np.exp(-(y-179)/7)))
    samples = np.arange(w)[None, :, None] + (np.arange(32)+.5)[None, None, :]/32
    alpha = (samples < edge[:, None, None]).mean(axis=2)
    background = np.broadcast_to(np.array([80., 150, 180]), (h, w, 3)).copy()
    background += np.linspace(0, 8, w)[None, :, None]
    foreground = np.broadcast_to(np.array([170., 130, 110]), (h, w, 3)).copy()
    foreground[103:143] = [105, 70, 75]
    foreground[45:65, 65:73] = [70, 65, 60]
    rgb = alpha[:, :, None]*foreground + (1-alpha[:, :, None])*background
    rgb += np.random.default_rng(243).normal(0, 2., size=rgb.shape)
    rgb = np.clip(np.rint(rgb), 0, 255).astype(np.uint8)
    if direction == -1:
        rgb, edge = rgb[:, ::-1].copy(), w-edge
    return rgb, np.c_[edge, y]
