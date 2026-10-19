from pathlib import Path
import sys
import unittest
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'tools')]
from identity_gauge_0247 import compensate_camera, canonicalize_centroid_radius, split_similarity_fields
from video_model_0241 import project


class IdentityGaugeTests(unittest.TestCase):
    def test_full_centroid_radius_jacobian_and_pair_shape_invariance(self):
        rng = np.random.default_rng(247)
        ref = rng.normal(size=(25, 3))*.03
        basis = rng.normal(size=(25, 3, 6))*.002
        beta = rng.normal(size=6)*.2
        v = ref+np.einsum('vck,k->vc', basis, beta)
        skin = np.arange(20)
        result, analytic, transform = canonicalize_centroid_radius(v, basis, ref, skin)
        numerical = np.empty_like(analytic)
        for k in range(6):
            delta = basis[:, :, k]*1e-6
            numerical[:, :, k] = (canonicalize_centroid_radius(v+delta, basis, ref, skin)[0]
                - canonicalize_centroid_radius(v-delta, basis, ref, skin)[0])/2e-6
        np.testing.assert_allclose(analytic, numerical, atol=1e-9, rtol=1e-5)
        np.testing.assert_allclose(result[skin].mean(0), ref[skin].mean(0), atol=1e-14)
        np.testing.assert_allclose(np.linalg.norm(np.diff(result, axis=0), axis=1),
            transform[0, 0]*np.linalg.norm(np.diff(v, axis=0), axis=1), atol=1e-14)

    def test_camera_compensation_preserves_projection(self):
        vertices = np.array([[.1, .2, .1], [-.1, .02, .03], [0, -.1, -.1]])
        a = .1
        q = np.array([[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1.]])
        transform = np.eye(4)
        transform[:3, :3], transform[:3, 3] = 1.2*q, [.03, .02, -.01]
        e = np.c_[np.eye(3), [0, 0, 1.]]
        k = np.array([[900., 0, 360], [0, 900, 640], [0, 0, 1.]])
        new = vertices@transform[:3, :3].T+transform[:3, 3]
        np.testing.assert_allclose(project(new, compensate_camera(e, transform), k), project(vertices, e, k), atol=1e-12)
        transform[0, 0] *= -1
        with self.assertRaises(ValueError):
            compensate_camera(e, transform)

    def test_similarity_and_local_fields_are_orthogonal(self):
        rng = np.random.default_rng(248)
        v, b = rng.normal(size=(30, 3)), rng.normal(size=(30, 3, 12))
        q, global_map, local = split_similarity_fields(v, b)
        np.testing.assert_allclose(q.T@local, 0., atol=1e-14)
        np.testing.assert_allclose(q@global_map+local, b.reshape(-1, 12), atol=1e-14)
