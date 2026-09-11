import unittest
import numpy as np
from headfoundry.mesh_section import section_segments


class SectionTests(unittest.TestCase):
    def test_plane_and_support_survive_mesh_displacement(self):
        v=np.array([[-1,0,0],[1,0,0],[1,2,0],[-1,2,0]],float)
        f=np.array([[0,1,2],[0,2,3]])
        ids,w,p=section_segments(v,f,0,0.)
        self.assertEqual(p.shape,(2,2,3))
        np.testing.assert_allclose(p[:,:,0],0)
        np.testing.assert_allclose(w.sum(2),1)
        self.assertTrue(np.all(w>=0))
        moved=v+[3,4,5]
        np.testing.assert_allclose(np.einsum('nij,njk->nik',w,moved[f[ids]]),p+[3,4,5])
        np.testing.assert_allclose(p[0,1],p[1,0])

    def test_tangency_edge_empty_and_rejections(self):
        f=np.array([[0,1,2]])
        v=np.array([[0,0,0],[1,1,0],[1,0,1]],float)
        self.assertEqual(len(section_segments(v,f,0,0)[0]),0)
        self.assertEqual(section_segments(v,f,0,-1)[2].shape,(0,2,3))
        v[1,0]=0
        ids,w,p=section_segments(v,f,0,0)
        np.testing.assert_allclose(p[0],v[:2])
        with self.assertRaises(ValueError): section_segments(v,f.astype(float),0,0)
        with self.assertRaises(ValueError): section_segments(v,f,True,0)
        with self.assertRaises(ValueError): section_segments(v,f,0,float('nan'))
        v[2,0]=0
        with self.assertRaises(ValueError): section_segments(v,f,0,0)
