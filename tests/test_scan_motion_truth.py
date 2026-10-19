import unittest

import numpy as np

from headfoundry.camera import project
from headfoundry.epipolar import sampson_distance
from tools.scan_motion_truth_0230 import look_at_origin,sample_surface,fundamental_from_cameras


class ScanMotionTruthTests(unittest.TestCase):
    def test_proper_declared_cameras_and_known_nonplanar_epipolar_truth(self):
        a=look_at_origin([0,0,6])
        b=look_at_origin([1.,-.4,5.9])
        for e in (a,b):
            np.testing.assert_allclose(e[:,:3]@e[:,:3].T,np.eye(3),atol=1e-12)
            self.assertAlmostEqual(np.linalg.det(e[:,:3]),1.)
        points=np.random.default_rng(230).uniform(-.8,.8,(50,3))
        k=np.array([[1000.,0,360],[0,1000.,640],[0,0,1.]])
        # Source-only visual review establishes +Y, not -Y, as upright here.
        self.assertLess(project(k@a,np.array([[0.,.5,0]]))[0,1],640)
        f=fundamental_from_cameras(k,a,b)
        self.assertLess(sampson_distance(f,project(k@a,points),project(k@b,points)).max(),1e-8)

    def test_surface_area_sampling_replays_original_triangles(self):
        vertices=np.array([[0.,0,0],[2,0,0],[0,2,0],[0,0,1],[1,0,1],[0,1,1]])
        faces=np.array([[0,1,2],[3,4,5]])
        points,ids,weights=sample_surface(vertices,faces,1000)
        np.testing.assert_allclose(points,np.einsum('ni,nij->nj',weights,vertices[faces[ids]]),atol=1e-14)
        np.testing.assert_allclose(weights.sum(axis=1),1.)
        self.assertTrue((weights>=0).all())
        self.assertGreater(float(np.mean(ids==0)),.75)
        with self.assertRaises(ValueError):
            look_at_origin([0,0,0])


if __name__=='__main__':
    unittest.main()
