import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from prepare_video_only_0241 import forbid_patient_geometry, video_document


class VideoOnlyInputTests(unittest.TestCase):
    def test_video_subset_and_geometry_read_guard(self):
        item = {'id': 'real-case-001-video', 'path': 'only.mp4', 'allowed_uses': ['local_head_reconstruction_validation']}
        parent = {'purpose': 'local_head_reconstruction_validation', 'inputs': [item, {'id': 'real-case-001-skin', 'path': 'never.stl'}]}
        result = video_document(parent)
        self.assertEqual(result['inputs'], [item])
        self.assertFalse(result['patient_geometry_inputs'])
        self.assertFalse(result['training_allowed'])
        with self.assertRaises(ValueError):
            video_document({'purpose': 'commercial_head_reconstruction', 'inputs': [item]})
        pilot = Path(__file__).resolve().parents[1] / 'assets/private/real-capture-pilot-v1'
        forbid_patient_geometry(pilot / 'manifest.json', pilot)
        forbid_patient_geometry(pilot.parent / 'authorized-video.mp4', pilot)
        for path in (pilot / 'oracle.npz', pilot.parent / 'medical.stl', pilot / 'camera-baseline-0217/cameras.npz'):
            with self.assertRaises(PermissionError):
                forbid_patient_geometry(path, pilot)
