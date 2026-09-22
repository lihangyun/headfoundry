import tempfile
import unittest
import pickle
from pathlib import Path

import numpy as np

from headfoundry.flame import FlameIdentityModel
from headfoundry.manifest import sha256_file
from tools.prepare_flame_open import restricted_load


class FlameOpenTests(unittest.TestCase):
    def fixture(self, root: Path):
        path = root / "flame2023_Open.safe.npz"
        source = root / "FLAME2023Open.zip"; source.write_bytes(b"official archive fixture")
        model_path = root / "flame2023_Open.pkl"; model_path.write_bytes(b"official model fixture")
        readme = root / "FLAME2023_Open Readme.pdf"; readme.write_bytes(b"official readme fixture")
        template = np.array([[0., 0., 0.], [1., 0., 0.], [0., 1., 0.], [0., 0., 1.]])
        directions = np.zeros((4, 3, 300)); directions[1, 2, 0] = 0.25
        np.savez(path, v_template=template, shapedirs=directions, faces=[[0, 1, 2], [0, 3, 1]])
        return path, {
            "id": "FLAME-2023-Open",
            "source_url": "https://flame.is.tue.mpg.de/",
            "license_id": "CC-BY-4.0",
            "path": path.name,
            "sha256": sha256_file(path),
            "source_path": source.name,
            "source_sha256": sha256_file(source),
            "model_path": model_path.name,
            "model_sha256": sha256_file(model_path),
            "readme_path": readme.name,
            "readme_sha256": sha256_file(readme),
            "conversion_id": "numpy-safe-neutral-identity-v1",
            "reviewed_by": "fixture",
            "reviewed_at": "2026-09-21",
            "attribution": "FLAME, Li et al. 2017",
            "commercial_use": True,
            "changes_disclosed": True,
            "prohibited_uses_reviewed": True,
        }

    def test_exact_open_asset_and_neutral_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); _, record = self.fixture(root)
            model = FlameIdentityModel.from_asset_record(record, root)
            identity = np.zeros(300); identity[0] = 2
            result = model.neutral_vertices(identity)
            np.testing.assert_allclose(result[1], [1, 0, 0.5])
            np.testing.assert_allclose(result[[0, 2, 3]], model.template[[0, 2, 3]])

    def test_old_noncommercial_or_tampered_assets_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); path, record = self.fixture(root)
            for key, value in [("id", "FLAME-2023"), ("license_id", "research-only"),
                               ("commercial_use", False), ("conversion_id", "unknown"),
                               ("source_sha256", "not-a-digest")]:
                broken = dict(record); broken[key] = value
                with self.assertRaises(ValueError):
                    FlameIdentityModel.from_asset_record(broken, root)
            path.write_bytes(path.read_bytes() + b"tampered")
            with self.assertRaisesRegex(ValueError, "digest mismatch"):
                FlameIdentityModel.from_asset_record(record, root)

    def test_invalid_geometry_and_coefficients_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); path, record = self.fixture(root)
            np.savez(path, v_template=np.zeros((4, 3)), shapedirs=np.zeros((4, 3, 299)), faces=[[0, 1, 2]])
            record["sha256"] = sha256_file(path)
            with self.assertRaisesRegex(ValueError, "shapedirs"):
                FlameIdentityModel.from_asset_record(record, root)
            np.savez(path, v_template=np.zeros((4, 3)), shapedirs=np.zeros((4, 3, 300)), faces=[[0., 1., 2.]])
            record["sha256"] = sha256_file(path)
            with self.assertRaisesRegex(ValueError, "integer"):
                FlameIdentityModel.from_asset_record(record, root)
            _, record = self.fixture(root)
            model = FlameIdentityModel.from_asset_record(record, root)
            for coefficients in (np.zeros(299), np.full(300, np.nan), np.full(300, 3.01)):
                with self.assertRaises(ValueError):
                    model.neutral_vertices(coefficients)

    def test_restricted_pickle_accepts_arrays_and_rejects_globals(self):
        safe = pickle.dumps({"array": np.arange(3)}, protocol=5)
        np.testing.assert_array_equal(restricted_load(safe)["array"], np.arange(3))
        hostile = pickle.dumps(eval, protocol=4)
        with self.assertRaises((ValueError, pickle.UnpicklingError)):
            restricted_load(hostile)


if __name__ == "__main__":
    unittest.main()
