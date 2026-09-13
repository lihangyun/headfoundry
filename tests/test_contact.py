import unittest
import numpy as np
from headfoundry.contact import compress_vertical_gap


class ContactTests(unittest.TestCase):
    def test_monotone_compression_and_protected_exterior(self):
        y=np.unique(np.r_[np.linspace(-.3,.4,1001),0,.1])
        v=np.c_[np.zeros(len(y)),y,np.ones(len(y))]
        c=compress_vertical_gap(v,np.zeros(len(y)),np.full(len(y),.1),np.full(len(y),.9))
        self.assertTrue(np.all(np.diff(c[:,1])>0))
        np.testing.assert_array_equal(c[:,[0,2]],v[:,[0,2]])
        np.testing.assert_allclose(c[np.isin(y,[0,.1]),1],[.045,.055])
        protected=(y<=-.08)|(y>=.18)
        np.testing.assert_array_equal(c[protected],v[protected])
        np.testing.assert_array_equal(compress_vertical_gap(v,np.zeros(len(y)),np.ones(len(y)),np.zeros(len(y))),v)
        np.testing.assert_array_equal(v[:,1],y)

    def test_reject_invalid_gap_and_amount(self):
        v=np.zeros((2,3));u=np.zeros(2);l=np.ones(2);s=np.full(2,.5)
        for args in [(v,u,u,s),(v,u,l,[1,.5]),(v,u,l,[-.1,.5]),(v,u,[np.nan,1],s),(v,u[:1],l,s)]:
            with self.assertRaises(ValueError):compress_vertical_gap(*args)
        with self.assertRaises(ValueError):compress_vertical_gap(v,u,l,s,falloff=0)
