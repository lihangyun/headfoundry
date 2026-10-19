"""Strict identity/rights boundary for the Apache checkpoint,never default NC."""
from pathlib import Path
import json
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from headfoundry.manifest import sha256_file

REPOSITORY = 'facebook/map-anything-apache'
REVISION = '00f9c245bbcb60522d1ed7f9e9d88462c6e3f38a'
WEIGHT_SHA = 'fa06c0fdccefc5048e072c85935d5789b1e36b307f3859033c17f9dcb9fd5201'
WEIGHT_SIZE = 4914062480
CONFIG_SHA = '65701d09d99ed37a21d295f0d138978b3d584ab3bccdbcb4a2853da212b676c5'
SOURCE_REVISION = '3d10cf7a3016fc0f9bb13a071ee66c47b10be0d9'
DINO_REVISION = '7764ea0f912e53c92e82eb78a2a1631e92725fc8'
DPT_REVISION = 'cd3fe90bb4c48577535cc4d51b602acca688a2ee'


def validate_identity(record, require_runtime=True):
    errors = []
    for key, expected in {'repository': REPOSITORY, 'revision': REVISION, 'license_id': 'Apache-2.0',
            'sha256': WEIGHT_SHA, 'size_bytes': WEIGHT_SIZE, 'config_sha256': CONFIG_SHA,
            'source_revision': SOURCE_REVISION, 'dino_revision': DINO_REVISION, 'dpt_revision': DPT_REVISION}.items():
        if record.get(key) != expected:
            errors.append(key+': exact reviewed Apache identity required')
    for key in ('rights_reviewed_by', 'rights_reviewed_at', 'model_card_path', 'model_card_sha256', 'license_evidence'):
        if not record.get(key):
            errors.append(key+': missing')
    if record.get('commercial_use') is not True:
        errors.append('commercial_use: explicit true required')
    if record.get('inference_upload_allowed') is not False:
        errors.append('inference_upload_allowed: explicit false required')
    if require_runtime and record.get('runtime_clearance') != 'TECHNICAL_CHECK_PASSED':
        errors.append('runtime_clearance: dependency/code path not cleared')
    return errors


def validate_assets(record, root, require_runtime=True):
    errors = validate_identity(record, require_runtime)
    root = Path(root).resolve()
    for key in ('path', 'config_path', 'model_card_path'):
        path = (root/str(record.get(key, ''))).resolve()
        expected = record.get({'path': 'sha256', 'config_path': 'config_sha256', 'model_card_path': 'model_card_sha256'}[key])
        if not path.is_relative_to(root) or not path.is_file():
            errors.append(key+': missing or outside locked asset root')
        elif not expected or sha256_file(path) != expected:
            errors.append(key+': hash mismatch')
    def checked_path(value, digest=None):
        path = (root/str(value or '')).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError('missing file or asset path escape')
        if digest is not None and sha256_file(path) != digest:
            raise ValueError('file hash mismatch')
        return path
    try:
        source_path = checked_path(record.get('source_tree_hashes_path'), record.get('source_tree_hashes_sha256', ''))
        source = json.loads(source_path.read_text(encoding='utf-8'))
        if not source:
            raise ValueError('empty source hash inventory')
        for name, digest in source.items():
            checked_path(name, digest)
        for name in record['license_evidence']:
            path = checked_path(name)
            if name != record['model_card_path'] and source.get(name) != sha256_file(path):
                raise ValueError('license evidence absent from pinned inventory')
        if require_runtime:
            review_path = checked_path(record.get('runtime_review_path'), record.get('runtime_review_sha256', ''))
            review = json.loads(review_path.read_text(encoding='utf-8'))
            adapter = ROOT/'tools/mapanything_permissive_runtime_0248.py'
            if (Path(record.get('runtime_adapter_path', '')).resolve() != adapter.resolve()
                    or sha256_file(adapter) != record.get('runtime_adapter_sha256')
                    or review.get('adapter_sha256') != record.get('runtime_adapter_sha256')
                    or review.get('strict_checkpoint_load_status') != 'TECHNICAL_CHECK_PASSED'
                    or review.get('state_tensor_count') != 736
                    or review.get('expanded_model_key_count') != 812
                    or review.get('verified_publisher_alias_count') != 76
                    or review.get('parameter_dtype') != 'float32'):
                raise ValueError('runtime strict-load evidence or adapter identity changed')
    except (KeyError, ValueError, TypeError, OSError) as error:
        errors.append('source/runtime evidence: '+str(error))
    return errors
