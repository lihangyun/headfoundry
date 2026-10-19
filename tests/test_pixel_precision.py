import unittest

import numpy as np

from tools.measure_pixel_precision_0226 import evaluate_pixels


class PixelPrecisionTests(unittest.TestCase):
    def test_known_translation_and_paired_cohort_reporting(self):
        source=np.arange(160,dtype=float).reshape(80,2)
        truth=source+[2.3,-1.7]
        raw=truth+[4.,0]
        eligible=np.ones(80,bool)
        eligible[:10]=False
        refined=truth.copy()
        refined[:10]=np.nan
        matrix=np.array([[1.,0,2.3],[0,1,-1.7],[0,0,1]])
        report,expected,_,_=evaluate_pixels(source,raw,refined,eligible,matrix)
        self.assertEqual(report['status'],'TECHNICAL_CHECK_PASSED')
        np.testing.assert_allclose(expected,truth)
        self.assertEqual(report['baseline_same_eligible_ids']['count'],70)
        self.assertAlmostEqual(report['baseline_same_eligible_ids']['p95_px'],4.)
        self.assertAlmostEqual(report['candidate_eligible']['p95_px'],0.)
        report,_,_,_=evaluate_pixels(source,raw,refined+2,eligible,matrix)
        self.assertEqual(report['status'],'REJECT')

    def test_missing_support_or_infinite_transform_cannot_pass(self):
        points=np.zeros((10,2))
        report,_,_,_=evaluate_pixels(points,points,points,np.ones(10,bool),np.eye(3))
        self.assertEqual(report['status'],'REJECT')
        with self.assertRaises(ValueError):
            evaluate_pixels(points,points,points,np.ones(10,bool),np.zeros((3,3)))


if __name__=='__main__':
    unittest.main()
