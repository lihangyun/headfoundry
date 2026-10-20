import io
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from audit_video_source import box_metadata, self_check
from intake_real_capture import video_review


class VideoInputIdentityTests(unittest.TestCase):
    def test_metadata_bounds_and_no_invented_camera(self):
        self.assertTrue(all(self_check().values()))
        payload = struct.pack('>I4sQ', 1, b'mdat', 19)+b'abc'
        result = box_metadata(io.BytesIO(payload), len(payload))
        self.assertEqual(result['atoms'][0]['bytes'], 19)
        self.assertFalse(result['camera_key_candidates'])
        self.assertEqual(result['calibration_status'], 'UNVERIFIED')

    def test_full_box_keys_are_not_intrinsic_calibration(self):
        def box(name, data):
            return struct.pack('>I4s', 8+len(data), name)+data
        key = b'com.example.camera.focal'
        table = b'\0'*4+struct.pack('>I', 1)+struct.pack('>I4s', len(key)+8, b'mdta')+key
        data = box(b'moov', box(b'meta', b'\0'*4+box(b'keys', table)))
        result = box_metadata(io.BytesIO(data), len(data))
        self.assertEqual(result['camera_key_candidates'], [key.decode()])
        self.assertEqual(result['calibration_status'], 'UNVERIFIED')

    def test_intake_reads_sequentially_and_never_trusts_seek_index(self):
        class Capture:
            def __init__(self, early=False):
                self.next, self.released, self.early = 0, False, early
            def isOpened(self):
                return True
            def get(self, key):
                return {cv2.CAP_PROP_FPS: 30., cv2.CAP_PROP_FRAME_COUNT: 20,
                    cv2.CAP_PROP_FRAME_WIDTH: 12, cv2.CAP_PROP_FRAME_HEIGHT: 16}.get(key, 9999.)
            def set(self, *args):
                raise AssertionError('Seeking must not be used for identity')
            def read(self):
                if self.next >= (8 if self.early else 20):
                    return False, None
                value = self.next*10
                self.next += 1
                return True, np.full((16, 12, 3), value, np.uint8)
            def release(self):
                self.released = True
        capture = Capture()
        with tempfile.TemporaryDirectory() as directory, patch('intake_real_capture.cv2.VideoCapture', return_value=capture):
            output = Path(directory)
            report = video_review('fixture-not-opened', output)
            self.assertEqual(len(report['frames']), 16)
            for entry in report['frames']:
                with Image.open(output/entry['path']) as image:
                    self.assertEqual(image.getpixel((0, 0)), (entry['frame']*10,)*3)
                self.assertEqual(entry['decoded_ordinal'], entry['frame'])
        self.assertTrue(capture.released)
        early = Capture(True)
        with tempfile.TemporaryDirectory() as directory, patch('intake_real_capture.cv2.VideoCapture', return_value=early):
            with self.assertRaises(ValueError):
                video_review('fixture-not-opened', Path(directory))
        self.assertTrue(early.released)
