import sys
from pathlib import Path
import unittest

import cv2
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from headfoundry.camera import project
from scan_motion_truth_0230 import look_at_origin
from nonplanar_context_0231 import symmetric_line_errors
from nonplanar_refinement_0233 import refine_nonplanar
from check_nonplanar_images_0233 import opaque_interior
from temporal_video_sfm_0220 import refine_step


class NonplanarRefinementTests(unittest.TestCase):
    def test_image_residual_does_not_snap_measurements_to_context_lines(self):
        image=np.random.default_rng(233).integers(0,256,(512,512),dtype=np.uint8)
        image=cv2.GaussianBlur(image,(5,5),1)
        world=np.random.default_rng(234).uniform(-.8,.8,(80,3))
        k=np.array([[900.,0,256],[0,900.,256],[0,0,1.]])
        a=look_at_origin([0,0,6])
        b=a.copy()
        b[:,3]+=[.2,0,0]
        context_a,context_b=project(k@a,world),project(k@b,world)
        points=np.array([[180.,180],[220,190],[270,200],[180,260],[230,250],[280,270]],np.float32)
        # Image motion deliberately violates the contextual horizontal epipolar
        # lines. A real image measurement must be allowed to reveal that error.
        moved=cv2.warpAffine(image,np.float32([[1,0,17.3],[0,1,-12.7]]),(512,512))
        result=refine_nonplanar(image,moved,context_a,context_b,points,points+[17.,-13.])
        self.assertTrue(result['eligible'].all(),result.get('refinement_failure'))
        self.assertLess(np.linalg.norm(result['pixels']-(points+[17.3,-12.7]),axis=1).max(),.3)
        self.assertGreater(symmetric_line_errors(result['fundamental'],points,result['pixels']).min(),10)
        native=refine_nonplanar(image,moved,context_a,context_b,points,points+[17.,-13.],refiner=refine_step)
        self.assertTrue(native['eligible'].all(),native.get('refinement_failure'))
        self.assertLess(np.linalg.norm(native['pixels']-(points+[17.3,-12.7]),axis=1).max(),.3)
        self.assertGreater(symmetric_line_errors(native['fundamental'],points,native['pixels']).min(),10)

    def test_missing_context_never_falls_back_to_a_pass(self):
        image=np.zeros((64,64),np.uint8)
        result=refine_nonplanar(image,image,np.ones((12,2)),np.ones((12,2)),np.array([[30.,30.]]),np.array([[30.,30.]]))
        self.assertFalse(result['eligible'].any())
        self.assertIn('refinement_failure',result)

    def test_foreground_interior_is_defined_without_endpoint_errors(self):
        alpha=np.zeros((80,80),np.uint8)
        alpha[10:70,10:70]=255
        pixels=np.array([[40.,40.],[20.,40.],[21.,40.],[68.,40.],[-1.,40.]])
        np.testing.assert_array_equal(opaque_interior(pixels,alpha),[True,False,True,False,False])


if __name__=='__main__':
    unittest.main()
