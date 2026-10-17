import sys
from pathlib import Path
import unittest
import tempfile

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from experiment_0210 import surface_samples, transform, safe_update
from headfoundry.surface_diagnostic import write_obj


class SurfaceRegistrationTests(unittest.TestCase):
    def test_uniform_triangle_samples_and_rigid_contract(self):
        v = np.array([[0., 0., 0.], [1., 0., 0.], [0., 1., 0.]])
        f = np.array([[0, 1, 2]])
        p, n = surface_samples(v, f, 10000, 210)
        np.testing.assert_allclose(p.mean(0), [1/3, 1/3, 0], atol=.01)
        self.assertTrue(np.all(p >= 0))
        self.assertTrue(np.all(p[:, :2].sum(1) <= 1+1e-12))
        np.testing.assert_allclose(n, np.tile([0., 0., 1.], (len(n), 1)))
        np.testing.assert_array_equal(p, surface_samples(v, f, 10000, 210)[0])
        params = np.array([0., 0., 0., .1, -.2, .3, np.log(2)])
        np.testing.assert_allclose(transform(v, params), v*2+params[3:6])

    def test_safe_update_backtracks_without_hiding_final_state(self):
        v = np.array([[0., 0., 0.], [1., 0., 0.], [0., 1., 0.]])
        f = np.array([[0, 1, 2]])
        fitted, halvings = safe_update(v, v+[0., 0., 1.], v, f)
        self.assertEqual(halvings, 4)
        np.testing.assert_allclose(fitted, v+[0., 0., .0625])
        with self.assertRaises(ValueError):
            surface_samples(v, f.astype(float), 10, 210)
        with self.assertRaises(ValueError):
            surface_samples(v*0, f, 10, 210)

    def test_optional_export_precision_preserves_a_near_boundary_mesh(self):
        v = np.array([[0., 0., 0.], [1., 0., 0.], [0., .5000002026943738, 0.]])
        f = np.array([[0, 1, 2]])
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(dir=root / "tmp") as directory:
            path = Path(directory) / "mesh.obj"
            write_obj(path, v, f, precision=17)
            actual = np.array([[float(a) for a in line.split()[1:]]
                               for line in path.read_text().splitlines() if line.startswith("v ")])
            np.testing.assert_array_equal(actual, v)
            with self.assertRaises(FileExistsError):
                write_obj(path, v, f)
            with self.assertRaises(ValueError):
                write_obj(Path(directory) / "invalid.obj", v, f, precision=7)


if __name__ == "__main__":
    unittest.main()
