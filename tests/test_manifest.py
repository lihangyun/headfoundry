import hashlib
import tempfile
import unittest
from pathlib import Path

from headfoundry.inputs import validate_multiview
from headfoundry.manifest import validate_manifest
from headfoundry.vggt import CommercialVGGTAdapter


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class ManifestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        inputs = []
        for index, yaw in enumerate((-60, -30, 0, 30, 60)):
            data = f"owned-photo-{index}".encode()
            path = self.root / f"view-{index}.jpg"
            path.write_bytes(data)
            inputs.append({
                "id": f"view-{index}", "path": path.name, "sha256": digest(data),
                "width_px": 1600, "height_px": 1200, "clarity_score": 0.8, "yaw_degrees": yaw,
                "source": "consented subject capture", "license_id": "subject-release-1",
                "allowed_uses": ["commercial_head_reconstruction"], "retention_until": "2027-09-01",
                "deletion_process": "delete source and derived biometric data on withdrawal",
                "consent": {"subject_id": "subject-1", "record_id": "consent-1", "granted_at": "2026-09-01", "biometric_processing": True},
            })
        model_data = b"deterministic fake checkpoint"
        (self.root / "model.safetensors").write_bytes(model_data)
        self.model = {
            "id": "VGGT-1B-Commercial", "repository": "facebook/VGGT-1B-Commercial",
            "path": "model.safetensors", "sha256": digest(model_data), "license_id": "vggt-aup-license",
            "accepted_by": "authorized-licensee", "accepted_at": "2026-09-01",
            "acceptable_use_reviewed": True, "military_use": False,
        }
        self.document = {"schema_version": 1, "purpose": "commercial_head_reconstruction", "inputs": inputs, "models": [self.model]}

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_complete_manifest_and_capture_pass(self) -> None:
        self.assertEqual(validate_manifest(self.document, self.root), [])
        self.assertEqual(validate_multiview(self.document["inputs"])["status"], "TECHNICAL_CHECK_PASSED")
        self.assertTrue(CommercialVGGTAdapter.from_asset_record(self.model, self.root).checkpoint.is_file())

    def test_missing_consent_fails_closed(self) -> None:
        del self.document["inputs"][0]["consent"]
        self.assertTrue(any("consent" in error for error in validate_manifest(self.document, self.root)))

    def test_local_validation_cannot_expand_input_consent(self) -> None:
        self.document["purpose"] = "local_head_reconstruction_validation"
        errors = validate_manifest(self.document, self.root)
        self.assertTrue(any("allowed_uses" in error for error in errors))
        for record in self.document["inputs"]:
            record["allowed_uses"] = ["local_head_reconstruction_validation"]
        self.assertEqual(validate_manifest(self.document, self.root), [])

    def test_noncommercial_checkpoint_is_rejected(self) -> None:
        self.model["id"] = "VGGT-1B"
        self.model["repository"] = "facebook/VGGT-1B"
        with self.assertRaisesRegex(ValueError, "only VGGT-1B-Commercial"):
            CommercialVGGTAdapter.from_asset_record(self.model, self.root)

    def test_duplicate_blurry_and_missing_coverage_are_reported(self) -> None:
        records = self.document["inputs"]
        records[1]["sha256"] = records[0]["sha256"]
        records[2]["clarity_score"] = 0.1
        records[4]["yaw_degrees"] = 20
        report = validate_multiview(records)
        self.assertEqual(report["status"], "REJECT")
        self.assertEqual({item["code"] for item in report["errors"]}, {"DUPLICATE", "BLUR", "VIEW_COVERAGE"})


if __name__ == "__main__":
    unittest.main()
