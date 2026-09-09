import unittest
import numpy as np
from headfoundry.mesh_clip import clip_below


class ClipTest(unittest.TestCase):
    def test_shared_plane_boundary_and_preserved_vertices(self):
        v=np.array([[0.,0,0],[1,0,0],[0,1,0],[0,0,1]])
        f=np.array([[0,2,1],[0,1,3],[0,3,2],[1,2,3]])
        c,faces,source=clip_below(v,f,1,.5)
        np.testing.assert_array_equal(c[source>=0],v[source[source>=0]])
        self.assertEqual(int((source<0).sum()),3)
        edges=np.sort(np.concatenate([faces[:,[0,1]],faces[:,[1,2]],faces[:,[2,0]]]),axis=1)
        unique,counts=np.unique(edges,axis=0,return_counts=True)
        self.assertTrue((counts<=2).all())
        np.testing.assert_allclose(c[unique[counts==1],1],.5)
        self.assertTrue((c[:,1]<=.5).all())
        unchanged,_,ids=clip_below(v,f,1,2)
        np.testing.assert_array_equal(unchanged,v[ids])
        with self.assertRaises(ValueError):clip_below(v,f,1,-1)
        with self.assertRaises(ValueError):clip_below(v,f,1,float('nan'))

    def test_plane_through_existing_vertex(self):
        v=np.array([[0.,0,0],[1,-1,0],[0,1,0]])
        c,f,_=clip_below(v,np.array([[0,1,2]]),1,0)
        self.assertEqual(len(f),1)
        self.assertEqual(len(c),3)
