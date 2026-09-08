import unittest
import numpy as np
from headfoundry.radial_surface import fit_radial_shell


class RadialSurfaceTest(unittest.TestCase):
    def test_closed_shell_and_unsupported_regions(self):
        rng=np.random.default_rng(8);theta=rng.uniform(-1.5,1.5,4000);y=rng.uniform(-.9,.9,4000)
        radius=np.sqrt(1-y*y)
        p=np.c_[radius*np.sin(theta),y,-radius*np.cos(theta)]
        v,f,report=fit_radial_shell(p,16,24)
        self.assertTrue(np.isfinite(v).all())
        edges=np.sort(np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]),axis=1)
        _,counts=np.unique(edges,axis=0,return_counts=True)
        self.assertTrue((counts==2).all())
        self.assertGreater(len(report['prior_only_vertices']),2)
        with self.assertRaises(ValueError):fit_radial_shell(np.ones((30,3)))
