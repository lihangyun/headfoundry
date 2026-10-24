import sys
from pathlib import Path
import unittest

import cv2
import numpy as np
from PIL import Image
from scipy.spatial.transform import Rotation

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from lingbot_camera import crop_transform, native_camera


class CameraContract(unittest.TestCase):
    def test_pil_center_affine_and_actual_crop(self):
        affine, shape, resized, top = crop_transform(720, 1280)
        self.assertEqual((shape, resized, top), ((518, 518), (518, 924), 203))
        # Independent floating ramp reveals PIL's sample-center geometry.
        ramp = np.broadcast_to(np.arange(1280, dtype=np.float32)[:, None], (1280, 720)).copy()
        output = np.asarray(Image.fromarray(ramp).resize(resized, Image.Resampling.BICUBIC))[top:top+518]
        native = (np.arange(518)-affine[1, 2])/affine[1, 1]
        np.testing.assert_allclose(output[10:-10, 200], native[10:-10], atol=.03)

    def test_c2w_and_native_projection(self):
        rot = Rotation.from_euler('xyz', [12, -23, 8], degrees=True)
        pose = np.r_[[.3, -.4, 1.2], rot.as_quat(), [.8, 1.1]]
        k, w2c = native_camera(pose, 720, 1280)
        points_camera = np.array([[.1, .2, 2.], [-.3, .1, 4.], [.2, -.1, 3.]])
        points_world = rot.apply(points_camera)+pose[:3]
        rvec, _ = cv2.Rodrigues(w2c[:, :3])
        actual, _ = cv2.projectPoints(points_world, rvec, w2c[:, 3], k, None)
        model = points_camera[:, :2]/points_camera[:, 2:]
        model *= [259/np.tan(1.1/2), 259/np.tan(.8/2)]
        model += 259
        affine = crop_transform(720, 1280)[0]
        expected = np.linalg.solve(affine, np.c_[model, np.ones(3)].T).T[:, :2]
        np.testing.assert_allclose(actual[:, 0], expected, atol=1e-10)
        np.testing.assert_allclose(w2c[:, :3]@pose[:3]+w2c[:, 3], 0, atol=1e-12)

    def test_invalid_prediction(self):
        for pose in (np.zeros(9), np.full(9, np.nan), np.zeros(8),
                     np.r_[np.zeros(3), [0, 0, 0, 1], [0, 1]]):
            with self.assertRaises(ValueError):
                native_camera(pose, 720, 1280)


if __name__ == '__main__':
    unittest.main()
