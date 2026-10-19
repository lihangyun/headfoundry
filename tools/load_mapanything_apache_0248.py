"""Offline strict F32 checkpoint construction test;no image inference or training."""
import ctypes
import json
import os
from pathlib import Path
import sys
import time
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'tools')]
from headfoundry.manifest import sha256_file
from mapanything_assets_0248 import validate_assets
from mapanything_permissive_runtime_0248 import (ASSET, install_permissive_runtime,
    audit_imported_provenance, meta_parameter_construction, expand_verified_parameter_aliases)

OUTPUT_NAME = 'strict-checkpoint-probe-interface-replay' if '--interface-replay' in sys.argv else 'strict-checkpoint-probe'


def main():
    output = ASSET/OUTPUT_NAME
    if output.exists():
        raise FileExistsError('Preserve first strict checkpoint construction')
    started = time.perf_counter()
    lock_path = ASSET/'asset-lock.json'
    lock = json.loads(lock_path.read_text(encoding='utf-8'))
    dependency = json.loads((ASSET/'permissive-runtime-probe/report.json').read_text(encoding='utf-8'))
    if validate_assets(lock, ASSET, require_runtime=False) or dependency['dependency_probe_status'] != 'TECHNICAL_CHECK_PASSED':
        raise ValueError('Exact cleared checkpoint bytes and prior dependency probe required')
    source_hashes = json.loads((ASSET/lock['source_tree_hashes_path']).read_text(encoding='utf-8'))
    if sha256_file(ASSET/lock['source_tree_hashes_path']) != lock['source_tree_hashes_sha256']:
        raise ValueError('Source identity manifest changed')
    for name, digest in source_hashes.items():
        if sha256_file(ASSET/name) != digest:
            raise ValueError('Pinned source file changed:'+name)
    output.mkdir()
    os.environ['HF_HUB_OFFLINE'] = '1'
    os.environ['TORCH_HOME'] = str(ASSET/'torch-cache')
    sys.dont_write_bytecode = True

    def audit(event, args):
        if event == 'socket.connect':
            raise PermissionError('Strict checkpoint load is offline,no implicit downloads')
    sys.addaudithook(audit)
    import torch
    from safetensors import safe_open
    from safetensors.torch import load_file
    torch.set_num_threads(4)
    runtime = install_permissive_runtime()
    sys.path.insert(0, str(ASSET/'source/mapanything'))
    from mapanything.models import MapAnything
    config = json.loads((ASSET/'weights/config.json').read_text(encoding='utf-8'))
    # Same override as the publisher's _from_pretrained:full checkpoint already
    # contains encoder weights. Never fetch a redundant encoder checkpoint.
    config['encoder_config']['torch_hub_pretrained'] = False
    with meta_parameter_construction():
        model = MapAnything(**config)
    with safe_open(str(ASSET/'weights/model.safetensors'), framework='pt', device='cpu') as archive:
        file_shapes = {key: list(archive.get_slice(key).get_shape()) for key in archive.keys()}
        publisher_aliases = archive.metadata() or {}
    state = load_file(str(ASSET/'weights/model.safetensors'), device='cpu')
    expanded, aliases = expand_verified_parameter_aliases(model, state, publisher_aliases)
    loaded = model.load_state_dict(expanded, strict=True, assign=True)
    if loaded.missing_keys or loaded.unexpected_keys or any(p.device.type == 'meta' or p.dtype != torch.float32 for p in model.parameters()):
        raise ValueError('Full F32 learned parameter assignment failed')
    model.eval()
    provenance = audit_imported_provenance()
    result = {'strict_checkpoint_load_status': 'TECHNICAL_CHECK_PASSED', 'runtime_clearance': 'TECHNICAL_CHECK_PASSED',
        'head_acceptance': 'UNVERIFIED', 'image_inference_run': False, 'training_run': False,
        'state_tensor_count': len(state), 'expanded_model_key_count': len(expanded),
        'verified_publisher_alias_count': len(aliases), 'verified_publisher_aliases': aliases,
        'parameter_count': sum(p.numel() for p in model.parameters()),
        'parameter_dtype': 'float32', 'device': 'cpu', 'dino_calls': runtime['dino_calls'],
        'imported_provenance': provenance, 'asset_lock_before_sha256': sha256_file(lock_path),
        'adapter_sha256': sha256_file(ROOT/'tools/mapanything_permissive_runtime_0248.py'),
        'producer_sha256': sha256_file(Path(__file__)), 'torch': torch.__version__,
        'elapsed_seconds': time.perf_counter()-started,
        'limits': 'Strict tensor compatibility and permissive source path only;MIT runtime variant numerical/geometry accuracy still UNVERIFIED.'}
    if time.perf_counter()-started > 180:
        raise TimeoutError('Strict checkpoint construction budget exhausted')
    path = output/'report.json'
    path.write_text(json.dumps(result, indent=2), encoding='utf-8')
    lock.update(runtime_clearance='TECHNICAL_CHECK_PASSED', runtime_review_path=str(path.relative_to(ASSET)),
        runtime_review_sha256=sha256_file(path), runtime_adapter_path=str((ROOT/'tools/mapanything_permissive_runtime_0248.py').resolve()),
        runtime_adapter_sha256=result['adapter_sha256'])
    lock_path.write_text(json.dumps(lock, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k != 'imported_provenance'}), flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        output = ASSET/OUTPUT_NAME
        if output.exists():
            (output/'failure.json').write_text(json.dumps({'status': 'REJECT', 'error': str(error)}, indent=2), encoding='utf-8')
        raise
