import unittest
import numpy as np
from headfoundry.flame import FlameIdentityModel
from headfoundry.flame_expression import FlameExpressionModel


class FlameExpressionTests(unittest.TestCase):
    def setUp(self):
        template=np.array([[0.,0.,0.],[1.,0.,0.],[0.,1.,0.]])
        shape=np.zeros((3,3,300));shape[0,0,0]=.2
        expression=np.zeros((3,3,100));expression[2,1,0]=.3
        self.model=FlameExpressionModel(FlameIdentityModel(template,shape,np.array([[0,1,2]])),expression)

    def test_shared_identity_separate_expression(self):
        beta=np.zeros(300);beta[0]=1
        expression=np.zeros(100);expression[0]=.5
        neutral=self.model.identity.neutral_vertices(beta)
        np.testing.assert_array_equal(self.model.vertices(beta,np.zeros(100)),neutral)
        changed=self.model.vertices(beta,expression)
        self.assertAlmostEqual(changed[2,1]-neutral[2,1],.15)
        np.testing.assert_array_equal(self.model.vertices(beta,np.zeros(100)),neutral)
        np.testing.assert_array_equal(changed[:2],neutral[:2])

    def test_invalid_expression_rejected(self):
        for expression in [np.zeros(99),np.full(100,np.nan),np.full(100,4.)]:
            with self.assertRaises(ValueError):self.model.vertices(np.zeros(300),expression)
        with self.assertRaises(ValueError):
            FlameExpressionModel(self.model.identity,np.zeros((3,3,99))).validate()
