import unittest
import numpy as np
from headfoundry.subdivision import catmull_clark, refine_triangle_attachments


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

    def test_refined_attachments_pin_chart_vertices_and_follow_affine_transforms(self):
        v=np.array([[0,0,0],[1,0,0],[0,1,0],[0,0,1]],float)
        f=np.array([[0,2,1],[0,1,3],[1,2,3],[2,0,3]])
        face_ids=np.array([0,0,2]);weights=np.array([[1,0,0],[1/3]*3,[.2,.3,.5]])
        refined,triangles,ids,bary=refine_triangle_attachments(v,f,face_ids,weights)
        points=np.einsum('ni,nij->nj',bary,refined[ids])
        np.testing.assert_allclose(points[0],refined[0])
        # Tetrahedron has four vertices/six edges; parent face0's inserted center
        # keeps index10 during the second refinement.
        np.testing.assert_allclose(points[1],refined[10])
        self.assertTrue(all(any(np.array_equal(q,face) for face in triangles) for q in ids))
        self.assertTrue(np.all(bary>=0));np.testing.assert_allclose(bary.sum(1),1)
        transform=np.array([[2,1,0],[0,3,1],[1,0,4]])
        shifted,other,other_ids,other_bary=refine_triangle_attachments(v@transform+[3,7,5],f,face_ids,weights)
        np.testing.assert_array_equal(triangles,other);np.testing.assert_array_equal(ids,other_ids)
        np.testing.assert_allclose(other_bary,bary)
        actual=np.einsum('ni,nij->nj',other_bary,shifted[other_ids])
        np.testing.assert_allclose(actual,points@transform+[3,7,5])

    def test_refined_attachments_reject_invalid_face_or_weights(self):
        v=np.array([[0,0,0],[1,0,0],[0,1,0]],float);f=np.array([[0,1,2]])
        for face,weights in [([1],[[1,0,0]]),([0.],[[1,0,0]]),([0],[[.2,.2,.2]]),
                             ([0],[[-.1,.5,.6]]),([0],[[np.nan,0,1]])]:
            with self.assertRaises(ValueError):refine_triangle_attachments(v,f,face,weights)
