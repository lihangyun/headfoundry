import unittest
import numpy as np
from headfoundry.surface_diagnostic import fit_surface


class SurfaceTests(unittest.TestCase):
    def setUp(self):
        self.prior=np.array([[-1.,-1.,0],[1,-1,0],[1,1,0],[-1,1,0],[0,0,-.2]])
        self.triangles=np.array([[0,1,4],[1,2,4],[2,3,4],[3,0,4]])
        self.p=np.array([[[500,0,0,0],[0,500,0,0],[0,0,1,5]],
                         [[500,0,0,-250],[0,500,0,0],[0,0,1,5]]],float)

    def uv(self,points):
        h=np.einsum('vij,nj->vni',self.p,np.c_[points,np.ones(len(points))])
        return h[:,:,:2]/h[:,:,2:]

    def test_preserves_boundary_and_recovers_depth(self):
        target=self.prior.copy();target[4,2]=-.4
        candidate=fit_surface(self.prior,self.uv(target),self.p,self.triangles,[0,1,2,3],.1)
        np.testing.assert_array_equal(candidate[:4],self.prior[:4])
        self.assertLess(np.linalg.norm(candidate-target),.02)

    def test_identical_input_is_fixed_point(self):
        candidate=fit_surface(self.prior,self.uv(self.prior),self.p,self.triangles,[0,1,2,3])
        np.testing.assert_allclose(candidate,self.prior,atol=1e-10)

    def test_triangle_barycentric_observation(self):
        target=self.prior.copy();target[4,2]=-.4
        ids=np.array([0,1,4]);w=np.array([.1,.2,.7]);point=w@target[ids];constraints=[]
        for view,p in enumerate(self.p):
            h=p@np.r_[point,1];constraints.append((view,ids,w,h[:2]/h[2]))
        result=fit_surface(self.prior,self.uv(self.prior),self.p,self.triangles,[0,1,2,3],.1,
                           observation_mask=np.zeros((2,5),bool),edge_observations=constraints)
        self.assertLess(np.linalg.norm(result-target),.02)

    def test_weighted_edge_constraint(self):
        target=self.prior.copy();target[4,2]=-.4
        ids=np.array([0,4]);weights=np.array([.3,.7]);point=weights@target[ids]
        observations=[]
        for view,p in enumerate(self.p):
            h=p@np.r_[point,1];observations.append((view,ids,weights,h[:2]/h[2]))
        candidate=fit_surface(self.prior,self.uv(self.prior),self.p,self.triangles,[0,1,2,3],.1,
                              observation_mask=np.zeros((2,5),bool),edge_observations=observations)
        self.assertLess(np.linalg.norm(candidate-target),.02)
        with self.assertRaises(ValueError):
            fit_surface(self.prior,self.uv(self.prior),self.p,self.triangles,[],edge_observations=[(0,ids,[1,1],[0,0])])

    def test_camera_behind_surface_rejected(self):
        self.p[:,2,3]=-5
        with self.assertRaises(ValueError):
            fit_surface(self.prior,np.zeros((2,5,2)),self.p,self.triangles,[0,1,2,3])

    def test_ray_constrained_depth_retains_frontal_pixels(self):
        center=np.linalg.solve(self.p[0,:,:3],-self.p[0,:,3])
        rays=self.prior-center
        target=self.prior.copy();target[4]+=rays[4]*-.04
        candidate=fit_surface(self.prior,self.uv(target),self.p,self.triangles,[0,1,2,3],.1,
                              displacement_directions=rays)
        np.testing.assert_allclose(self.uv(candidate)[0],self.uv(self.prior)[0],atol=1e-10)
        self.assertLess(np.linalg.norm(candidate-target),.02)
        for bad in [rays*0,rays*np.nan,rays[:2]]:
            with self.assertRaises(ValueError):
                fit_surface(self.prior,self.uv(target),self.p,self.triangles,[],displacement_directions=bad)
