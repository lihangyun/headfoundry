import unittest

import numpy as np

from headfoundry.camera import estimate_projection_dlt, invert_camera_poses, project, synthetic_camera_check


class CameraTests(unittest.TestCase):
    def test_pose_inverse_roundtrip_and_invalid_frames(self):
        angle = .43
        c, s = np.cos(angle), np.sin(angle)
        poses = np.repeat(np.eye(4)[None], 2, axis=0)
        poses[0, :3, :3] = [[c, 0, s], [0, 1, 0], [-s, 0, c]]
        poses[:, :3, 3] = [[.3, -.1, 2], [-.4, .2, 3]]
        extrinsics = invert_camera_poses(poses)
        points_camera = np.array([[.1, .4, 2], [-.2, .1, 3]])
        world = np.einsum("vij,nj->vni", poses[:, :3, :3], points_camera) + poses[:, None, :3, 3]
        recovered = np.einsum("vij,vnj->vni", extrinsics[:, :, :3], world) + extrinsics[:, None, :, 3]
        np.testing.assert_allclose(recovered, np.broadcast_to(points_camera, (2, 2, 3)), atol=1e-12)
        for change in ("reflection", "scale", "homogeneous", "nonfinite"):
            invalid = poses.copy()
            if change == "reflection": invalid[:, :3, 0] *= -1
            elif change == "scale": invalid[:, :3, :3] *= 2
            elif change == "homogeneous": invalid[:, 3, 0] = 1
            else: invalid[0, 0, 0] = np.nan
            with self.assertRaises(ValueError):
                invert_camera_poses(invalid)
        with self.assertRaises(ValueError):
            invert_camera_poses(poses[:, :3])

    def test_synthetic_camera_is_subpixel(self) -> None:
        result = synthetic_camera_check()
        self.assertTrue(result.passed)
        self.assertLess(result.p95_reprojection_px, 0.05)

    def test_rejects_too_few_correspondences(self) -> None:
        with self.assertRaises(ValueError):
            estimate_projection_dlt(np.zeros((5, 3)), np.zeros((5, 2)))

    def test_project_preserves_principal_point(self) -> None:
        intrinsic = np.array(
            [[1000.0, 0.0, 320.0], [0.0, 1000.0, 240.0], [0.0, 0.0, 1.0]]
        )
        camera = intrinsic @ np.column_stack([np.eye(3), np.array([[0.0], [0.0], [3.0]])])
        result = project(camera, np.array([[0.0, 0.0, 0.0]]))
        np.testing.assert_allclose(result, [[320.0, 240.0]])


if __name__ == "__main__":
    unittest.main()
