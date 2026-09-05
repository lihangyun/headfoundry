import unittest
import numpy as np
from scipy.spatial.transform import Rotation
from headfoundry.bundle import fit, project


def fixture():
    rng = np.random.default_rng(29)
    shape = rng.uniform(-.7, .7, (16, 3))
    rv = np.array([[0, 0, 0], [.03, -.6, .02], [-.02, .6, -.03], [.02, 1., 0]])
    translations = np.tile([0., 0., 5.], (4, 1))
    k = np.tile([[1100., 0, 600], [0, 1100., 600], [0, 0, 1]], (4, 1, 1))
    uv = project(shape, Rotation.from_rotvec(rv).as_matrix(), translations, k)
    validation = np.zeros((4, 16), bool)
    for view in range(4):
        validation[view, view*2:view*2+2] = True
    return dict(shape_prior=shape+rng.normal(0, .015, shape.shape), observations=uv,
                train_mask=~validation, validation_mask=validation, intrinsics=k,
                rotation_vectors=rv, translations=translations)


class BundleTests(unittest.TestCase):
    def test_prior_source_cannot_leak_into_validation(self):
        data = fixture()
        data['view_names'] = ['front', 'left', 'right', 'profile']
        data['prior_source_views'] = ['front']
        with self.assertRaises(ValueError):
            fit(data)

    def test_heldout_projection_recovery(self):
        result = fit(fixture())
        self.assertLess(result['validation_p95_px'], .2)
        self.assertEqual(result['status'], 'UNVERIFIED')

    def test_heldout_error_is_not_hidden_by_training_fit(self):
        data = fixture()
        data['observations'][data['validation_mask']] += 30
        result = fit(data)
        self.assertGreater(result['validation_p95_px'], 30)
        self.assertFalse(result['validation_threshold_passed'])

    def test_overlapping_masks_rejected(self):
        data = fixture()
        data['train_mask'][:] = True
        with self.assertRaises(ValueError):
            fit(data)
