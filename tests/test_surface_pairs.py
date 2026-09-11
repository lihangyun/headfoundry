import unittest
import numpy as np
from headfoundry.surface_diagnostic import fit_surface


class PairTests(unittest.TestCase):
    def test_relative_closure_protection_and_translation(self):
        v=np.array([[0,0,2],[1,0,2],[0,1,2],[0,0,3],[1,0,3],[0,1,3]],float)
        f=np.array([[0,1,2],[3,4,5]])
        pair=(f[0],[1,0,0],f[1],[1,0,0],[0,0,.2],100.)
        def solve(mesh,pairs):
            return fit_surface(mesh,np.empty((0,6,2)),np.empty((0,3,4)),f,[1,2,4,5],regularization=1.,surface_pairs=pairs)
        c=solve(v,[pair])
        np.testing.assert_array_equal(c[[1,2,4,5]],v[[1,2,4,5]])
        np.testing.assert_allclose(c[3]-c[0],[0,0,.2],atol=1e-3)
        np.testing.assert_allclose(c[[0,3]].mean(0),v[[0,3]].mean(0),atol=1e-9)
        np.testing.assert_allclose(solve(v+[7,8,9],[pair]),c+[7,8,9],atol=1e-8)
        np.testing.assert_allclose(solve(v,[]),v)
        for bad in [(f[0],[2,0,0],f[1],[1,0,0],[0,0,0],1.),(f[0],[1,0,0],f[1],[1,0,0],[0,0,0],0.)]:
            with self.assertRaises(ValueError):solve(v,[bad])
