from collections import Counter
import unittest
import numpy as np
from headfoundry.patch import triangulate_disk,harmonic_depth,improve_diagonals


class PatchTests(unittest.TestCase):
    def test_diagonal_improvement_preserves_boundary_area_and_inputs(self):
        p=np.array([[0,0],[2,0],[2,1],[0,.1]],float)
        f=np.array([[0,1,2],[0,2,3]])
        for faces in [f,f[:,::-1]]:
            source=faces.copy();candidate=improve_diagonals(p,faces)
            np.testing.assert_array_equal(faces,source)
            def boundary(q):
                counts=Counter(tuple(sorted(edge)) for t in q for edge in zip(t,np.roll(t,-1)))
                return {edge for edge,n in counts.items() if n==1}
            self.assertEqual(boundary(candidate),boundary(source))
            self.assertNotEqual({tuple(sorted(x)) for x in candidate},{tuple(sorted(x)) for x in source})
            def areas(q):
                a=p[q[:,1]]-p[q[:,0]];b=p[q[:,2]]-p[q[:,0]]
                return a[:,0]*b[:,1]-a[:,1]*b[:,0]
            self.assertAlmostEqual(areas(candidate).sum(),areas(source).sum())
            self.assertTrue(np.all(areas(candidate)*areas(source)[0]>0))
            np.testing.assert_array_equal(improve_diagonals(p,candidate),candidate)
        for invalid in [np.array([[0,0,1]]),np.array([[0,1,2],[0,1,2]]),np.array([[0,1,9]])]:
            with self.assertRaises(ValueError):improve_diagonals(p,invalid)

    def test_metric_harmonic_extension_reproduces_affine_depth(self):
        p=np.array([[0,0],[1,0],[1,1],[0,1],[.1,.2]],float)
        f=np.array([[0,1,4],[1,2,4],[2,3,4],[3,0,4]])
        expected=3+p@np.array([2.,-4.])
        np.testing.assert_allclose(harmonic_depth(p,f,expected[:4]),expected,atol=1e-12)
        np.testing.assert_allclose(harmonic_depth(p*17,f[:,::-1],expected[:4]),expected,atol=1e-12)
        np.testing.assert_array_equal(harmonic_depth(p,f,expected),expected)
        with self.assertRaises(ValueError):harmonic_depth(np.r_[p,[[2,2]]],f,expected[:4])
        with self.assertRaises(ValueError):harmonic_depth(p,np.array([[0,0,1]]),expected[:4])

    def test_concave_boundary_and_disk_topology(self):
        boundary=np.array([[0,0],[3,0],[3,3],[2,3],[2,1],[1,1],[1,3],[0,3]],float)
        for b in (boundary,boundary[::-1]):
            v,f=triangulate_disk(b,.3)
            np.testing.assert_array_equal(v[:len(b)],b)
            counts=Counter(tuple(sorted(edge)) for t in f for edge in zip(t,np.roll(t,-1)))
            expected={tuple(sorted((i,(i+1)%len(b)))) for i in range(len(b))}
            self.assertEqual({edge for edge,n in counts.items() if n==1},expected)
            self.assertTrue(all(x in (1,2) for x in counts.values()))
            self.assertEqual(len(v)-len(counts)+len(f),1)
            a=v[f[:,1]]-v[f[:,0]];c=v[f[:,2]]-v[f[:,0]];cross=a[:,0]*c[:,1]-a[:,1]*c[:,0]
            self.assertTrue(np.all(cross>0) or np.all(cross<0))
            self.assertAlmostEqual(abs(cross.sum())/2,7.)

    def test_invalid_boundaries(self):
        b=np.array([[0,0],[1,0],[1,1],[0,1]],float)
        for boundary,spacing in [(b[[0,2,1,3]],1),(np.r_[b,b[:1]],1),(b,0),(b,np.nan),
                                  (b*np.nan,1),([[0,0],[1,0],[2,0]],1)]:
            with self.assertRaises(ValueError):triangulate_disk(boundary,spacing)

    def test_collinear_vertices_are_retained_and_refinement_is_conforming(self):
        b=np.array([[0,0],[1,0],[2,0],[2,2],[0,2]],float)
        v,f=triangulate_disk(b,.2)
        np.testing.assert_array_equal(v[:5],b)
        oriented=Counter((int(a),int(c)) for t in f for a,c in zip(t,np.roll(t,-1)))
        boundary={(i,(i+1)%5) for i in range(5)}
        for edge,count in oriented.items():
            self.assertEqual(count,1)
            if edge not in boundary:self.assertEqual(oriented[edge[::-1]],1)
        area=np.cross(np.c_[v[f[:,1]]-v[f[:,0]],np.zeros(len(f))],np.c_[v[f[:,2]]-v[f[:,0]],np.zeros(len(f))])[:,2]
        self.assertTrue(np.all(area>0));self.assertAlmostEqual(area.sum()/2,4.)
