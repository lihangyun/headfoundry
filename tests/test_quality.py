import unittest

from headfoundry.quality import evaluate


PASSING = {
    "camera": {"landmark_reprojection_p95_px": 2.0},
    "geometry": {
        "scan_point_to_surface_p95_mm": 1.5,
        "profile_silhouette_iou": 0.96,
        "frontal_landmark_nme": 0.02,
    },
    "texture": {"heldout_lpips": 0.18, "seam_delta_e_p95": 5.0},
    "mesh": {"non_manifold_edges": 0, "degenerate_faces": 0, "flipped_faces": 0},
    "evidence": {
        "licensed_benchmark": True,
        "heldout_visual_review": True,
        "complete_reconstruction": True,
    },
}


class QualityTests(unittest.TestCase):
    def test_all_gates_must_pass(self) -> None:
        self.assertEqual(evaluate(PASSING)["status"], "ACCEPT")

    def test_metrics_without_visual_evidence_are_only_partial(self) -> None:
        metrics_only = {key: value for key, value in PASSING.items() if key != "evidence"}
        self.assertEqual(evaluate(metrics_only)["status"], "PARTIAL_SUCCESS")

    def test_missing_metric_fails_closed(self) -> None:
        incomplete = {**PASSING, "texture": {"heldout_lpips": 0.18}}
        self.assertEqual(evaluate(incomplete)["status"], "REJECT")

    def test_one_failed_metric_rejects_candidate(self) -> None:
        failed = {**PASSING, "mesh": {**PASSING["mesh"], "non_manifold_edges": 1}}
        self.assertEqual(evaluate(failed)["status"], "REJECT")


if __name__ == "__main__":
    unittest.main()
