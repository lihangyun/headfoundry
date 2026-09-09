import unittest
import numpy as np
from tools.prepare_makehuman_head import extract_head


class HeadTemplateTest(unittest.TestCase):
    def test_eye_helpers_are_explicit_and_other_helpers_stay_excluded(self):
        text='v 0 6 1\nv 1 6 1\nv 0 7 1\ng body\nf 1 2 3\ng helper-l-eye\nf 1 2 3\ng helper-r-eye\nf 1 2 3\ng helper-hair\nf 1 2 3\n'
        self.assertEqual(len(extract_head(text)[1]),1)
        self.assertEqual(len(extract_head(text,include_eye_helpers=True)[1]),3)
        with self.assertRaises(ValueError):
            extract_head(text.replace('g helper-r-eye','g unwanted'),include_eye_helpers=True)

    def test_helpers_excluded_crop_and_rigid_axes(self):
        text='v 0 6 1\nv 1 6 1\nv 1 7 1\nv 0 7 1\nv 0 0 1\ng body\nf 1/1 2/2 3/3 4/4\nf 1 2 5\ng helper-hair\nf 1 2 3\n'
        v,f,used=extract_head(text)
        self.assertEqual(len(f),2)
        np.testing.assert_array_equal(used,[0,1,2,3])
        np.testing.assert_array_equal(v[0],[0,-6,-1])
        with self.assertRaises(ValueError):extract_head(text,minimum_y=9)
