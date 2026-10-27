"""Bounded CPU-only strict loading; no forward pass, images, or network."""
import json
import os
import sys
from check_metric_bundle_0374 import BASE, ROOT, WEIGHT, main as verify_bundle


def worker():
    verify_bundle()
    import torch
    torch.set_num_threads(2)
    sys.path.insert(0, str(BASE / 'source/metric_depth'))
    from depth_anything_v2.dpt import DepthAnythingV2
    model = DepthAnythingV2(encoder='vits', features=64,
                           out_channels=[48, 96, 192, 384], max_depth=20.0).eval()
    state = torch.load(WEIGHT, weights_only=True, map_location='cpu')
    if not isinstance(state, dict) or not state:
        raise ValueError('empty/non-dictionary checkpoint')
    for key, tensor in state.items():
        if not isinstance(key, str) or not isinstance(tensor, torch.Tensor):
            raise ValueError('non-tensor checkpoint entry')
        if not torch.isfinite(tensor).all():
            raise ValueError('non-finite checkpoint')
    match = model.load_state_dict(state, strict=True)
    if match.missing_keys or match.unexpected_keys:
        raise ValueError('incomplete model')
    bad = dict(state)
    removed = next(iter(bad))
    del bad[removed]
    try:
        model.load_state_dict(bad, strict=True)
    except RuntimeError as error:
        if 'Missing key(s)' not in str(error):
            raise
    else:
        raise AssertionError('strict loader admitted missing key')
    result = dict(status='TECHNICAL_CHECK_PASSED', state_entries=len(state),
                  parameters=sum(p.numel() for p in model.parameters()),
                  dtypes=sorted({str(t.dtype) for t in state.values()}),
                  missing_key_control='REJECTED_AS_EXPECTED', device='cpu',
                  inference='NOT_RUN', accuracy='UNVERIFIED',
                  scope='architecture matching and finite tensors only')
    (BASE / 'strict-load.json').write_text(json.dumps(result, indent=2))
    print(json.dumps(result))


if __name__ == '__main__':
    if sys.argv[1:] == ['worker']:
        worker()
    else:
        from bounded_process import run
        env = os.environ.copy()
        env.update(CUDA_VISIBLE_DEVICES='', PYTHONDONTWRITEBYTECODE='1')
        result = run([str(ROOT / '.venv-metric0374/Scripts/python.exe'), __file__, 'worker'],
                     ROOT, env, BASE / 'strict-load.log', BASE / 'strict-load-worker.json',
                     120, 4 * 1024**3)
        print(result)
        sys.exit(0 if result['status'] == 'TECHNICAL_CHECK_PASSED' else 1)
