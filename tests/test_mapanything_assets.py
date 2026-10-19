from pathlib import Path
import sys
import unittest
import zipfile
import io
import json
import tempfile
from unittest.mock import patch
from headfoundry.manifest import sha256_file
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'tools')]
from mapanything_assets_0248 import (REPOSITORY, REVISION, WEIGHT_SHA, WEIGHT_SIZE, CONFIG_SHA,
    SOURCE_REVISION, DINO_REVISION, DPT_REVISION, validate_identity, validate_assets)
from install_mapanything_apache_0248 import safe_zip_members


class MapAnythingAssetTests(unittest.TestCase):
    def test_weight_license_is_not_runtime_clearance_and_no_nc_fallback(self):
        record = dict(repository=REPOSITORY, revision=REVISION, license_id='Apache-2.0', sha256=WEIGHT_SHA,
            size_bytes=WEIGHT_SIZE, config_sha256=CONFIG_SHA, source_revision=SOURCE_REVISION,
            dino_revision=DINO_REVISION, dpt_revision=DPT_REVISION, rights_reviewed_by='fixture',
            rights_reviewed_at='2026-10-19', model_card_path='card', model_card_sha256='f'*64,
            license_evidence=['fixture'], commercial_use=True, inference_upload_allowed=False, runtime_clearance='UNVERIFIED')
        self.assertFalse(validate_identity(record, require_runtime=False))
        self.assertTrue(validate_identity(record))
        for changes in ({'repository': 'facebook/map-anything'}, {'license_id': 'CC-BY-NC-4.0'},
                {'revision': 'main'}, {'commercial_use': False}, {'rights_reviewed_by': ''}, {'sha256': '0'*64}):
            self.assertTrue(validate_identity(dict(record, **changes), require_runtime=False))

    def test_source_archive_cannot_escape_private_asset_root(self):
        for name in ('../outside.py', '/outside.py', 'repo/C:/outside.py', 'repo/..\\outside.py'):
            data = io.BytesIO()
            with zipfile.ZipFile(data, 'w') as archive:
                archive.writestr(name, 'fixture')
            data.seek(0)
            with zipfile.ZipFile(data) as archive, self.assertRaises(ValueError):
                safe_zip_members(archive)

    def test_runtime_evidence_and_source_mutation_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory, patch('mapanything_assets_0248.validate_identity', return_value=[]):
            root = Path(directory)
            for name in ('weight', 'config', 'card', 'source', 'license'):
                (root/name).write_bytes(name.encode())
            source = {name: sha256_file(root/name) for name in ('source', 'license')}
            (root/'inventory').write_text(json.dumps(source), encoding='utf-8')
            adapter = ROOT/'tools/mapanything_permissive_runtime_0248.py'
            review = dict(adapter_sha256=sha256_file(adapter), strict_checkpoint_load_status='TECHNICAL_CHECK_PASSED',
                state_tensor_count=736, expanded_model_key_count=812, verified_publisher_alias_count=76, parameter_dtype='float32')
            (root/'review').write_text(json.dumps(review), encoding='utf-8')
            record = dict(path='weight', sha256=sha256_file(root/'weight'), config_path='config',
                config_sha256=sha256_file(root/'config'), model_card_path='card', model_card_sha256=sha256_file(root/'card'),
                source_tree_hashes_path='inventory', source_tree_hashes_sha256=sha256_file(root/'inventory'),
                license_evidence=['card', 'license'], runtime_review_path='review', runtime_review_sha256=sha256_file(root/'review'),
                runtime_adapter_path=str(adapter), runtime_adapter_sha256=sha256_file(adapter))
            self.assertFalse(validate_assets(record, root))
            self.assertTrue(validate_assets(dict(record, runtime_review_path='../review'), root))
            self.assertTrue(validate_assets(dict(record, runtime_adapter_sha256='0'*64), root))
            (root/'source').write_bytes(b'changed')
            self.assertTrue(validate_assets(record, root))
