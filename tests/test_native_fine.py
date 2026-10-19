import sys
from pathlib import Path
from types import SimpleNamespace
import unittest

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from native_fine_0238 import refine_native, unique_coordinates


class FakeNative:
    def __init__(self, reorder=False, mutate=False):
        self.net = SimpleNamespace(fine_matcher=self.logits)
        self.reorder, self.mutate = reorder, mutate

    def logits(self, features):
        logits = torch.zeros((len(features), 64))
        logits[0, 0] = logits[2, 0] = 10
        return logits

    def batch_match(self, a, b):
        return [(torch.tensor([0, 1, 2]), torch.tensor([2, 0, 1]))]

    def refine_matches(self, first, second, matches, batch_idx):
        a, b = matches[0]
        keep = torch.tensor([True, False, True])
        result = torch.cat([first['keypoints'][0, a[keep]] + torch.tensor([.25, -.5]), second['keypoints'][0, b[keep]]], dim=1)
        if self.reorder:
            result = result.flip(0)
        if self.mutate:
            second['keypoints'][0, 0, 0] += 1
        return result


class NativeFineTests(unittest.TestCase):
    def features(self, count=3):
        return {'keypoints': torch.arange(count * 2, dtype=torch.float32).reshape(1, count, 2),
            'descriptors': torch.ones((1, count, 64)), 'scales': torch.ones((1, count))}

    def test_native_order_confidence_and_fixed_reference(self):
        first, second = self.features(), self.features()
        result = refine_native(FakeNative(), first, second)
        np.testing.assert_array_equal(result['matches'], [[0, 2], [1, 0], [2, 1]])
        np.testing.assert_array_equal(result['native_keep'], [True, False, True])
        np.testing.assert_array_equal(result['source'], [[4., 5.], [0., 1.], [2., 3.]])
        np.testing.assert_allclose(result['refined'][[0, 2]], result['raw'][[0, 2]] + [.25, -.5])
        np.testing.assert_array_equal(second['keypoints'], self.features()['keypoints'])
        np.testing.assert_array_equal(unique_coordinates([[1., 2.], [3., 4.], [1., 2.]]), [False, True, False])

    def test_malformed_mutated_or_reordered_native_results_fail_closed(self):
        for native in (FakeNative(reorder=True), FakeNative(mutate=True)):
            with self.assertRaises(ValueError):
                refine_native(native, self.features(), self.features())
        bad = self.features()
        bad['scales'][0, 0] = 0
        with self.assertRaises(ValueError):
            refine_native(FakeNative(), bad, self.features())
        empty = refine_native(FakeNative(), self.features(0), self.features())
        self.assertEqual(empty['matches'].shape, (0, 2))
        self.assertEqual(len(empty['native_keep']), 0)


if __name__ == '__main__':
    unittest.main()
