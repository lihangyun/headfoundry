"""Strict offline construction/loading only. Does not run a forward pass."""
import hashlib
import json
import os
from pathlib import Path
import socket
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/private/lingbot-entry-0347'
SOURCE = ROOT / 'assets/private/lingbot-source-0346'


def worker():
    os.environ['HF_HUB_OFFLINE'] = '1'
    os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'
    receipt = json.loads((SOURCE / 'receipt.json').read_text(encoding='utf-8'))
    for entry in receipt['files']:
        data = (SOURCE / entry['path']).read_bytes()
        if hashlib.sha256(data).hexdigest() != entry['sha256']:
            raise ValueError('source identity mismatch')
    weight = OUT / 'lingbot-map.pt'
    with weight.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    if digest != 'ee665103348e07e6b826d529b8e61de8f413d5432a4f2e84970d6c8fd2e1cd72':
        raise ValueError('checkpoint identity mismatch')
    sys.path.insert(0, str(SOURCE))
    import torch
    from lingbot_map.models.gct_stream import GCTStream
    from lingbot_map.aggregator.base import AggregatorBase
    from lingbot_map.layers.vision_transformer import vit_large
    torch.set_num_threads(4)
    torch.manual_seed(0)

    def no_pretrained(self, patch_embed, img_size, patch_size, num_register_tokens,
                      embed_dim, pretrained_path, interpolate_antialias=True,
                      interpolate_offset=0.0, block_chunks=0, init_values=1.0):
        # Same fixed architecture; optional independent DINO loading is removed.
        if patch_embed != 'dinov2_vitl14_reg' or pretrained_path is not None:
            raise ValueError('unexpected backbone configuration')
        self.patch_embed = vit_large(img_size=img_size, patch_size=patch_size,
            num_register_tokens=num_register_tokens,
            interpolate_antialias=interpolate_antialias,
            interpolate_offset=interpolate_offset, block_chunks=block_chunks,
            init_values=init_values)
        self._dino_checkpoint = None
        self.patch_embed.mask_token.requires_grad_(False)

    def deny_network(*args, **kwargs):
        raise RuntimeError('offline model worker attempted network')

    with patch.object(socket.socket, 'connect', deny_network), \
         patch.object(AggregatorBase, '_build_patch_embed', no_pretrained):
        print('constructing fixed CPU model', flush=True)
        model = GCTStream(pretrained_path=None, use_sdpa=True, enable_3d_rope=True,
                          camera_num_iterations=4, kv_cache_sliding_window=64)
        print('safe checkpoint read', flush=True)
        container = torch.load(weight, map_location='cpu', weights_only=True, mmap=True)
        state = container['model'] if 'model' in container else container
        expected = model.state_dict()
        missing = sorted(set(expected)-set(state))
        extra = sorted(set(state)-set(expected))
        wrong = [key for key in set(expected)&set(state)
                 if not isinstance(state[key], torch.Tensor) or state[key].shape != expected[key].shape]
        coverage = {'missing': missing, 'extra': extra, 'wrong_shape': wrong,
                    'expected_keys': len(expected), 'checkpoint_keys': len(state)}
        (OUT / 'state-coverage.json').write_text(json.dumps(coverage, indent=2), encoding='utf-8')
        if missing or extra or wrong:
            raise ValueError('strict state coverage failed')
        del expected
        model.load_state_dict(state, strict=True, assign=True)
        del state, container
        model.eval()
        if not torch.cuda.is_available():
            raise RuntimeError('registered CUDA device unavailable')
        torch.cuda.reset_peak_memory_stats()
        model.aggregator.to(dtype=torch.bfloat16)
        model.to('cuda')
        torch.cuda.synchronize()
        result = dict(status='TECHNICAL_CHECK_PASSED', meaning='strict loading only; no inference',
                      torch_version=torch.__version__, device=torch.cuda.get_device_name(),
                      parameter_count=sum(p.numel() for p in model.parameters()),
                      cuda_peak_bytes=torch.cuda.max_memory_allocated(), coverage=coverage)
        (OUT / 'load-result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
        print(json.dumps(result), flush=True)


if __name__ == '__main__':
    if sys.argv[1:] == ['--worker']:
        worker()
    elif not sys.argv[1:]:
        from bounded_process import run
        record = run([str(ROOT / '.venv-lingbot-0347/Scripts/python.exe'),
                      str(Path(__file__).resolve()), '--worker'], ROOT, dict(os.environ),
                     OUT / 'load.log', OUT / 'load-worker.json', 180, 16*1024**3)
        print(json.dumps(record))
    else:
        raise SystemExit('unsupported arguments')
