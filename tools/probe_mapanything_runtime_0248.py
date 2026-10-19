"""No checkpoint/image inference;test actual permissive dependency route first."""
import json
import os
from pathlib import Path
import sys
import time
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'tools')]
from mapanything_permissive_runtime_0248 import ASSET, install_permissive_runtime, audit_imported_provenance
from headfoundry.manifest import sha256_file


def main():
    output = ASSET/'permissive-runtime-probe'
    if output.exists():
        raise FileExistsError('Preserve first permissive runtime probe')
    started = time.perf_counter()
    output.mkdir()
    os.environ['HF_HUB_OFFLINE'] = '1'
    os.environ['TORCH_HOME'] = str(ASSET/'torch-cache')
    sys.dont_write_bytecode = True

    def audit(event, args):
        if event == 'socket.connect':
            raise PermissionError('Runtime probe is offline;no uploads or implicit downloads')
    sys.addaudithook(audit)
    import torch
    from torch import nn
    from torch.nn import functional as f
    torch.set_num_threads(4)
    torch.manual_seed(248)
    runtime = install_permissive_runtime()
    block = runtime['provider'].make_fusion_block(8)
    a, b = torch.randn(1, 8, 4, 6), torch.randn(1, 8, 4, 6)
    unit1, unit2 = block.resConfUnit1, block.resConfUnit2
    reference = a+b+unit1.conv2(f.relu(unit1.conv1(f.relu(b))))
    reference = reference+unit2.conv2(f.relu(unit2.conv1(f.relu(reference))))
    reference = block.out_conv(f.interpolate(reference, scale_factor=2, mode='bilinear', align_corners=True))
    difference = float((block(a, b)-reference).abs().max())
    if difference > 1e-6:
        raise ValueError('Original MIT DPT and explicit residual/fusion computation disagree')
    sys.path.insert(0, str(ASSET/'source/mapanything'))
    from mapanything.models import MapAnything
    provenance = audit_imported_provenance()
    result = {'dependency_probe_status': 'TECHNICAL_CHECK_PASSED', 'runtime_clearance': 'UNVERIFIED',
        'checkpoint_loaded': False, 'image_inference_run': False, 'head_acceptance': 'UNVERIFIED',
        'original_mit_dpt_reference_max_error': difference, 'model_class': str(MapAnything),
        'dino_calls': runtime['dino_calls'], 'imported_provenance': provenance,
        'producer_sha256': sha256_file(Path(__file__)),
        'adapter_sha256': sha256_file(ROOT/'tools/mapanything_permissive_runtime_0248.py'),
        'torch': torch.__version__, 'cuda_available': torch.cuda.is_available(), 'elapsed_seconds': time.perf_counter()-started,
        'limits': 'Dependencies/known tensor algebra only. Full checkpoint strict key/shape and geometric accuracy remain UNVERIFIED.'}
    (output/'report.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k != 'imported_provenance'}), flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        output = ASSET/'permissive-runtime-probe'
        if output.exists():
            (output/'failure.json').write_text(json.dumps({'status': 'REJECT', 'error': str(error)}, indent=2), encoding='utf-8')
        raise
