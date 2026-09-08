import tempfile
import unittest
from pathlib import Path
import numpy as np
from headfoundry.depth_surface import write_observed_obj
from tools.render_surface_orbit import read_surface, largest_component


class SurfaceOrbitTest(unittest.TestCase):
    def test_component_filter_does_not_deform(self):
        v=np.arange(21,dtype=float).reshape(7,3)
        f=np.array([[0,1,2],[1,2,3],[4,5,6]])
        actual_v,actual_f=largest_component(v,f)
        np.testing.assert_array_equal(actual_v,v[:4])
        np.testing.assert_array_equal(actual_f,f[:2])

    def test_export_roundtrip_and_invalid_indices(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'surface.obj'
            v=np.array([[0.,0.,1.],[1.,0.,1.],[0.,1.,1.]])
            f=np.array([[0,1,2]])
            write_observed_obj(path,v,f)
            actual_v,actual_f=read_surface(path)
            np.testing.assert_array_equal(v,actual_v)
            np.testing.assert_array_equal(f,actual_f)
            with self.assertRaises(FileExistsError):write_observed_obj(path,v,f)
            invalid=Path(directory)/'invalid.obj'
            write_observed_obj(invalid,v,np.array([[0,1,3]]))
            with self.assertRaises(ValueError):read_surface(invalid)
