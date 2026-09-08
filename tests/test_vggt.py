import unittest
from pathlib import Path

import numpy as np

from headfoundry.vggt import CameraInitialization, evaluate_camera_initialization, load_fixture


FIXTURE = Path(__file__).parent / "fixtures" / "vggt_camera_point_fixture.json"


class CommercialVGGTAdapterTests(unittest.TestCase):
    def test_deterministic_fixture_passes_camera_gate(self) -> None:
        result, image_sizes = load_fixture(FIXTURE)
        report = evaluate_camera_initialization(result, image_sizes)
        self.assertEqual(report["status"], "TECHNICAL_CHECK_PASSED")
        self.assertLess(report["camera"]["landmark_reprojection_p95_px"], 1e-9)
        self.assertEqual(report["coordinate_convention"], "opencv_camera_from_world_x_right_y_down_z_forward")

    def test_bad_matrix_format_rejects(self) -> None:
        result, image_sizes = load_fixture(FIXTURE)
        broken = CameraInitialization(
            result.extrinsics[:, :, :3], result.intrinsics, result.world_points,
            result.track_points_world, result.tracks_2d,
        )
        self.assertEqual(evaluate_camera_initialization(broken, image_sizes)["status"], "REJECT")

    def test_negative_depth_rejects_cheirality(self) -> None:
        result, image_sizes = load_fixture(FIXTURE)
        behind = CameraInitialization(
            result.extrinsics, result.intrinsics, -np.abs(result.world_points),
            result.track_points_world, result.tracks_2d,
        )
        report = evaluate_camera_initialization(behind, image_sizes)
        self.assertEqual(report["status"], "REJECT")
        self.assertFalse(next(item for item in report["checks"] if item["name"] == "cheirality")["passed"])

    def test_wrong_coordinate_convention_rejects(self) -> None:
        result, image_sizes = load_fixture(FIXTURE)
        wrong = CameraInitialization(
            result.extrinsics, result.intrinsics, result.world_points,
            result.track_points_world, result.tracks_2d, "camera_to_world",
        )
        self.assertEqual(evaluate_camera_initialization(wrong, image_sizes)["status"], "REJECT")

    def test_invalid_lower_intrinsics_and_hidden_tracks_reject(self) -> None:
        result, sizes = load_fixture(FIXTURE)
        k = result.intrinsics.copy();k[:,1,0] = 100
        wrong = CameraInitialization(result.extrinsics,k,result.world_points,result.track_points_world,result.tracks_2d)
        report = evaluate_camera_initialization(wrong,sizes)
        self.assertFalse(next(c for c in report['checks'] if c['name']=='intrinsic_and_focal_plausibility')['passed'])
        points = result.track_points_world.copy();points[0] = [0,0,-100]
        wrong = CameraInitialization(result.extrinsics,result.intrinsics,result.world_points,points,result.tracks_2d)
        report = evaluate_camera_initialization(wrong,sizes)
        self.assertEqual(report['status'],'REJECT')
        self.assertFalse(next(c for c in report['checks'] if c['name']=='track_cheirality')['passed'])

    def test_implausible_focal_length_rejects(self) -> None:
        result, image_sizes = load_fixture(FIXTURE)
        intrinsics = result.intrinsics.copy()
        intrinsics[0, 0, 0] = 10
        wrong = CameraInitialization(
            result.extrinsics, intrinsics, result.world_points,
            result.track_points_world, result.tracks_2d,
        )
        report = evaluate_camera_initialization(wrong, image_sizes)
        self.assertEqual(report["status"], "REJECT")
        self.assertFalse(next(item for item in report["checks"] if item["name"] == "intrinsic_and_focal_plausibility")["passed"])

    def test_inconsistent_tracks_reject(self) -> None:
        result, image_sizes = load_fixture(FIXTURE)
        inconsistent = CameraInitialization(
            result.extrinsics, result.intrinsics, result.world_points,
            result.track_points_world, result.tracks_2d + 10,
        )
        report = evaluate_camera_initialization(inconsistent, image_sizes)
        self.assertEqual(report["status"], "REJECT")


if __name__ == "__main__":
    unittest.main()
