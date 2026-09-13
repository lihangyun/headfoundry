import unittest
import numpy as np
from headfoundry.subdivision import catmull_clark


class SubdivisionTests(unittest.TestCase):
    def test_open_quad_boundary_orientation_and_affine_invariance(self):
        v=np.array([[0,0,0],[1,0,0],[1,1,0],[0,1,0]],float)
        f=[[0,1,2,3]];s,q=catmull_clark(v,f)
        self.assertEqual(s.shape,(9,3));self.assertEqual(q.shape,(4,4))
        np.testing.assert_allclose(s[:4,:2],[[.125,.125],[.875,.125],[.875,.875],[.125,.875]])
        np.testing.assert_allclose(s[8],[.5,.5,0])
        self.assertTrue(np.all(np.cross(s[q[:,1]]-s[q[:,0]],s[q[:,3]]-s[q[:,0]])[:,2]>0))
        transform=np.array([[2,1,0],[0,3,1],[1,0,4]])
        mapped,other=catmull_clark(v@transform+[3,7,5],f)
        np.testing.assert_allclose(mapped,s@transform+[3,7,5]);np.testing.assert_array_equal(q,other)
        self.assertEqual(catmull_clark(s,q)[1].shape,(16,4))

    def test_closed_cube_known_stencil(self):
        v=np.array([[-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1],[-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1]],float)
        f=[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
        s,q=catmull_clark(v,f)
        np.testing.assert_allclose(s[:8],v*5/9)
        self.assertEqual(len(s),26);self.assertEqual(len(q),24)
        refined,_=catmull_clark(s,q);self.assertTrue(np.isfinite(refined).all())

    def test_invalid_inputs_and_disconnected_fan(self):
        v=np.array([[0,0,0],[1,0,0],[1,1,0],[0,1,0],[2,0,0],[2,1,0]],float)
        for f in ([[0,1,1]],[[0,1,6]],[[0.,1.,2.]],[[0,1,2],[0,1,3]],
                  [[0,1,2],[0,3,4],[0,4,5]],[[0,1,2,3]]):
            with self.assertRaises(ValueError):catmull_clark(v,f)
        with self.assertRaises(ValueError):catmull_clark(v*np.nan,[[0,1,2]])

    def test_two_closed_fans_sharing_one_vertex_are_rejected(self):
        v=np.array([[0,0,0],[1,0,0],[0,1,0],[0,0,1],[-1,0,0],[0,-1,0],[0,0,-1]],float)
        tetra=[[0,2,1],[0,1,3],[1,2,3],[2,0,3]]
        other=[[0 if i==0 else i+3 for i in face] for face in tetra]
        with self.assertRaisesRegex(ValueError,'vertex fan'):catmull_clark(v,tetra+other)
