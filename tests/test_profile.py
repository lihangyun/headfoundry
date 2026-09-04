import unittest
from pathlib import Path

import numpy as np

from headfoundry.profile import evaluate_profile, fit_profile, load_fixture


FIXTURE = Path(__file__).parents[1] / "examples" / "profile_fixture.json"


class ProfileTests(unittest.TestCase):
    def test_profile_constraint_improves_editable_contour(self) -> None:
        _, baseline, target, editable = load_fixture(FIXTURE)
        candidate = fit_profile(baseline, target, editable)
        report = evaluate_profile(baseline, target, candidate, editable)
        self.assertEqual(report["status"], "TECHNICAL_CHECK_PASSED")
        self.assertGreaterEqual(report["profile"]["relative_improvement"], 0.5)

    def test_face_core_is_protected(self) -> None:
        _, baseline, target, editable = load_fixture(FIXTURE)
        candidate = fit_profile(baseline, target, editable)
        protected = np.setdiff1d(np.arange(len(baseline)), editable)
        np.testing.assert_array_equal(candidate[protected], baseline[protected])

    def test_invalid_contour_shape_rejects(self) -> None:
        with self.assertRaises(ValueError):
            fit_profile(np.zeros((3, 2)), np.zeros((4, 2)), np.array([1]))


if __name__ == "__main__":
    unittest.main()
