import unittest

import numpy as np

from headfoundry.normal_observation import normal_line_hits


class NormalObservationTests(unittest.TestCase):
    def setUp(self):
        self.vertices = np.array([[0., 0., 0.], [1., 0., 0.], [1., 1., 0.], [0., 1., 0.]])
        self.faces = np.array([[0, 1, 2], [0, 2, 3]])

    def test_both_signs_shared_edge_miss_and_range(self):
        points = np.array([[.5, .5, .05], [.2, .3, -.04], [2., 2., 0.], [.2, .3, .2]])
        hit, count = normal_line_hits(points, np.tile([0., 0., 1.], (4, 1)), self.vertices, self.faces)
        np.testing.assert_array_equal(count, [1, 1, 0, 0])
        np.testing.assert_allclose(hit[:2], [[.5, .5, 0.], [.2, .3, 0.]], atol=1e-14)
        self.assertTrue(np.isnan(hit[2:]).all())

    def test_ambiguous_layers_orientation_and_cutoff(self):
        vertices = np.vstack([self.vertices, self.vertices+[0., 0., .05]])
        faces = np.vstack([self.faces, self.faces+4])
        hit, count = normal_line_hits([[.2, .3, .025]], [[0., 0., 1.]], vertices, faces)
        self.assertEqual(count[0], 2)
        self.assertTrue(np.isnan(hit).all())
        for triangles, cutoff in ((self.faces[:, ::-1], np.inf), (self.faces, .2)):
            _, count = normal_line_hits([[.2, .3, .025]], [[0., 0., 1.]], self.vertices, triangles, max_y=cutoff)
            self.assertEqual(count[0], 0)

    def test_rejects_invalid_directions_and_degenerate_surface(self):
        with self.assertRaises(ValueError):
            normal_line_hits([[.2, .3, .05]], [[0., 0., 2.]], self.vertices, self.faces)
        with self.assertRaises(ValueError):
            normal_line_hits([[.2, .3, .05]], [[0., 0., 1.]], self.vertices, np.array([[0, 0, 1]]))


if __name__ == "__main__":
    unittest.main()
