import unittest

import cv2
import numpy as np

from tools.affine_patch_0227 import refine_affine_patches


class AffinePatchTests(unittest.TestCase):
    def test_known_affine_direction_and_subpixel_centers(self):
        image=np.random.default_rng(227).integers(0,256,(512,512),dtype=np.uint8)
        image=cv2.GaussianBlur(image,(5,5),1)
        points=np.array([[180.,180],[230,180],[280,180],[180,230],[230,230],[280,230]],np.float32)
        matrix=np.array([[1.01,.025,-5.2],[-.015,.99,4.3]],np.float32)
        expected=np.c_[points,np.ones(len(points))]@matrix.T
        moved=cv2.warpAffine(image,matrix,(512,512))
        result=refine_affine_patches(image,moved,points,expected+[.3,-.2])
        self.assertGreaterEqual(int(result['eligible'].sum()),5)
        self.assertLess(np.linalg.norm(result['pixels'][result['eligible']]-expected[result['eligible']],axis=1).max(),.3)
        # A random-texture patch may find a false local optimum; it must not
        # survive the existing cycle guard merely to make this fixture green.
        self.assertTrue((~result['eligible'][result['fb_error']>.75]).all())

    def test_missing_texture_and_invalid_inputs_fail_closed(self):
        image=np.zeros((64,64),np.uint8)
        result=refine_affine_patches(image,image,np.array([[32.,32]]),np.array([[32.,32]]))
        self.assertFalse(result['eligible'].any())
        with self.assertRaises(ValueError):
            refine_affine_patches(image,image,np.array([[np.nan,32.]]),np.array([[32.,32.]]))


if __name__=='__main__':
    unittest.main()
