import unittest
from unittest.mock import patch

import cv2
import numpy as np

from tools.temporal_video_sfm_0220 import resolve_keyframe_hashes, track_step, refine_step


class TemporalVideoTrackTests(unittest.TestCase):
    def test_known_translation_and_occlusion(self):
        image = np.random.default_rng(220).integers(0, 256, (512, 512), dtype=np.uint8)
        image = cv2.GaussianBlur(image, (5, 5), 1)
        mask = np.zeros_like(image)
        # Keep the known-motion check clear of the coarsest pyramid's border.
        mask[120:392, 120:392] = 255
        points = cv2.goodFeaturesToTrack(image, 80, .01, 8, mask=mask).reshape(-1, 2)
        moved = cv2.warpAffine(image, np.float32([[1, 0, 2], [0, 1, -1]]), (512, 512))
        predicted, keep, fb, _ = track_step(image, moved, points)
        self.assertGreater(keep.sum(), .9 * len(points))
        self.assertLess(np.linalg.norm(predicted[keep] - points[keep] - [2, -1], axis=1).max(), .15)
        self.assertLess(fb[keep].max(), .15)
        self.assertEqual(int(track_step(image, np.zeros_like(image), points)[1].sum()), 0)

    def test_invalid_or_empty_input(self):
        image = np.zeros((20, 20), np.uint8)
        self.assertEqual(len(track_step(image, image, np.empty((0, 2)))[0]), 0)
        with self.assertRaises(ValueError):
            track_step(image, image, np.array([[np.nan, 3.]]))

    def test_descriptor_initial_flow_is_used_in_both_directions(self):
        image = np.random.default_rng(226).integers(0,256,(512,512),dtype=np.uint8)
        image = cv2.GaussianBlur(image,(5,5),1)
        mask = np.zeros_like(image)
        mask[150:350,150:350] = 255
        points = cv2.goodFeaturesToTrack(image,60,.01,8,mask=mask).reshape(-1,2)
        moved = cv2.warpAffine(image,np.float32([[1,0,35.3],[0,1,-20.7]]),(512,512))
        initial = points + [35.,-21.]
        with patch.object(cv2,'calcOpticalFlowPyrLK',wraps=cv2.calcOpticalFlowPyrLK) as spy:
            predicted,keep,_,_ = track_step(image,moved,points,initial=initial)
        self.assertEqual(spy.call_count,2)
        for call in spy.call_args_list:
            self.assertEqual(call.kwargs['flags'],cv2.OPTFLOW_USE_INITIAL_FLOW)
            self.assertEqual(call.kwargs['maxLevel'],3)
            self.assertIsNotNone(call.args[3])
        self.assertGreater(keep.sum(),.9*len(points))
        self.assertLess(np.linalg.norm(predicted[keep]-points[keep]-[35.3,-20.7],axis=1).max(),.2)
        with self.assertRaises(ValueError):
            track_step(image,moved,points,initial=np.zeros((1,2)))

    def test_seeded_local_refinement_never_repeats_large_motion_search(self):
        image=np.random.default_rng(234).integers(0,256,(512,512),dtype=np.uint8)
        image=cv2.GaussianBlur(image,(5,5),1)
        mask=np.zeros_like(image)
        mask[150:330,150:330]=255
        points=cv2.goodFeaturesToTrack(image,60,.01,8,mask=mask).reshape(-1,2)
        moved=cv2.warpAffine(image,np.float32([[1,0,64.3],[0,1,-25.7]]),(512,512))
        initial=points+[64.,-26.]
        with patch.object(cv2,'calcOpticalFlowPyrLK',wraps=cv2.calcOpticalFlowPyrLK) as spy:
            predicted,keep,_,_=refine_step(image,moved,points,initial)
        self.assertEqual(spy.call_count,2)
        for call in spy.call_args_list:
            self.assertEqual(call.kwargs['maxLevel'],0)
            self.assertEqual(call.kwargs['flags'],cv2.OPTFLOW_USE_INITIAL_FLOW)
        self.assertGreater(keep.sum(),.9*len(points))
        self.assertLess(np.linalg.norm(predicted[keep]-points[keep]-[64.3,-25.7],axis=1).max(),.2)
        with self.assertRaises(ValueError):
            refine_step(image,moved,points,None)

    def test_exact_sequential_frame_identity_and_ambiguity(self):
        expected = {0: "a", 12: "b", 24: "c"}
        self.assertEqual(resolve_keyframe_hashes(expected, [(0, "a"), (13, "b"), (25, "c")]),
                         {0: 0, 12: 13, 24: 25})
        for decoded in ([(0, "a"), (12, "b")],
                        [(0, "a"), (1, "a"), (12, "b"), (24, "c")],
                        [(0, "a"), (15, "b"), (24, "c")]):
            with self.assertRaises(ValueError):
                resolve_keyframe_hashes(expected, decoded)


if __name__ == "__main__":
    unittest.main()
