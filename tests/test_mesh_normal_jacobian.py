import sys
from pathlib import Path
import unittest

import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from mesh_normal_jacobian import check,normals


class MeshNormalJacobianTest(unittest.TestCase):
    def test_owned_normal_and_complete_xyz_derivative_controls(self):
        result=check()
        self.assertEqual(result['status'],'TECHNICAL_CHECK_PASSED')
        self.assertEqual(result['central_steps'],[1e-6,5e-7])
        relative=np.asarray(result['per_column_relative_max'])
        self.assertEqual(relative.shape,(2,))
        self.assertTrue(np.isfinite(relative).all())
        self.assertLessEqual(float(relative.max()),1e-6)
        self.assertLessEqual(result['translation_null_max'],1e-12)
        self.assertLessEqual(result['scale_null_max'],1e-12)
        self.assertEqual(result['invalid_cases_rejected'],6)

    def test_complex_unused_and_cancelled_geometry_fail_closed(self):
        triangle=np.array([[0.,0.,0.],[1.,0.,0.],[0.,1.,0.]])
        faces=np.array([[0,1,2]])
        cases={'complex':(triangle.astype(complex),faces),
            'unused':(np.r_[triangle,[[2.,2.,2.]]],faces),
            'cancelled':(triangle,np.r_[faces,faces[:,::-1]])}
        for name,(vertices,indices) in cases.items():
            for derivatives in (True,False):
                with self.subTest(case=name,derivatives=derivatives),self.assertRaises(ValueError):
                    normals(vertices,indices,derivatives)

    def test_normals_only_returns_no_derivative(self):
        triangle=np.array([[0.,0.,0.],[1.,0.,0.],[0.,1.,0.]])
        unit,jac=normals(triangle,np.array([[0,1,2]],dtype=np.uint32),False)
        np.testing.assert_array_equal(unit,np.tile([0.,0.,1.],(3,1)))
        self.assertIsNone(jac)
