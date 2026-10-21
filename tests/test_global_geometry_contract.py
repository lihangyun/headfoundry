"""Generic synthetic math/holdout regression; no optional mapper dependency."""
import unittest

import numpy as np

from tools.check_global_geometry_contract import project, scene, similarity
from tools.check_dense_grid_contract import check
from tools.check_state_fingerprint import check as check_state_fingerprint
from tools.check_quadric_rank_contract import check as check_quadric_rank
from tools.batched_point_elimination import check as check_batched_points


class GlobalGeometryContractTests(unittest.TestCase):
    def test_batched_point_elimination_matches_scalar_with_missing_views(self):
        check_batched_points()

    def test_quadric_rank_three_not_rank_one_or_singular_pencil(self):
        check_quadric_rank()

    def test_exact_streaming_state_fingerprint(self):
        check_state_fingerprint()

    def test_dense_pixel_edge_center_and_invalid_queries(self):
        check()

    def test_visibility_holdout_and_similarity_gauge(self):
        xyz, centers, poses, k, observations = scene()
        self.assertEqual(len(xyz), 270)
        common = set(range(270))
        held_rows = 0
        for i, (ids, xy) in observations.items():
            common.intersection_update(ids)
            held_rows += int((ids % 5 == 0).sum())
            uv, depth = project(k, poses[i], xyz[ids])
            np.testing.assert_allclose(uv, xy+.5, atol=1e-12)
            self.assertTrue((depth > 0).all())
        self.assertFalse(common)
        self.assertEqual(held_rows, 162)
        angle = .2
        q = np.array([[np.cos(angle), -np.sin(angle), 0],
                      [np.sin(angle), np.cos(angle), 0], [0, 0, 1]])
        expected = 1.7*centers@q.T + [1., -.5, .3]
        s, r, t = similarity(centers[[0, 2, 4]], expected[[0, 2, 4]])
        np.testing.assert_allclose(s*centers@r.T+t, expected, atol=1e-12)
