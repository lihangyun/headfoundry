import sys
from pathlib import Path
import unittest

import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1] / "tools"))
from localize_direct_features_0225 import foreground_mask, unique_identity_mask


class DirectFeatureMaskTests(unittest.TestCase):
    def test_original_roi_color_and_eight_pixel_erosion(self):
        pixels=np.zeros((1280,720,3),np.uint8)
        pixels[:]=[0,0,100]
        pixels[520:780,200:500]=[180,100,100]
        pixels[:400]=[255,0,0]
        expected=np.zeros((1280,720),np.uint8)
        expected[528:772,208:492]=255
        np.testing.assert_array_equal(foreground_mask(pixels),expected)

    def test_missing_face_fails_closed(self):
        with self.assertRaises(ValueError):
            foreground_mask(np.zeros((1280,720,3),np.uint8))

    def test_identity_aliases_all_removed_without_best_copy_selection(self):
        np.testing.assert_array_equal(unique_identity_mask(np.array([9,2,9,4,2,7])),[False,False,False,True,False,True])
        np.testing.assert_array_equal(unique_identity_mask(np.array([],dtype=int)),[])
        with self.assertRaises(ValueError):
            unique_identity_mask(np.array([1.,2.]))


if __name__ == "__main__":
    unittest.main()
