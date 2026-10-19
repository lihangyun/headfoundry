import sys
from pathlib import Path
import unittest

import cv2
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from context_rectification_0228 import context_homography,refine_context_rectified


class ContextRectificationTests(unittest.TestCase):
    def test_local_image_measurement_corrects_a_biased_context_warp(self):
        image=np.random.default_rng(228).integers(0,256,(512,512),dtype=np.uint8)
        image=cv2.GaussianBlur(image,(5,5),1)
        y,x=np.mgrid[150:350:40,150:350:40]
        context=np.c_[x.ravel(),y.ravel()].astype(float)
        points=np.array([[180.,180],[220,190],[270,200],[180,260],[230,250],[280,270]],np.float32)
        moved=cv2.warpAffine(image,np.float32([[1,0,17.3],[0,1,-12.7]]),(512,512))
        # The context has a deliberate2px/-1px bias, not available truth.
        result=refine_context_rectified(image,moved,context,context+[15.3,-11.7],points,points+[17.,-13.])
        self.assertTrue(result['eligible'].all())
        expected=points+[17.3,-12.7]
        self.assertLess(np.linalg.norm(result['pixels']-expected,axis=1).max(),.2)
        self.assertGreater(np.linalg.norm(result['pixels']-(points+[15.3,-11.7]),axis=1).min(),1.5)
        np.testing.assert_allclose(result['context_matrix'][:2,2],[15.3,-11.7],atol=1e-4)

    def test_missing_or_unspread_context_fails_closed(self):
        with self.assertRaises(ValueError):
            context_homography(np.ones((12,2)),np.ones((12,2)))


if __name__=='__main__':
    unittest.main()
