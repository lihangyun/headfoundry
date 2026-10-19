"""Narrow BSD/Apache runtime plus ORIGINAL MIT DPT,never CroCo NC code.

Original DPT blocks: Intel ISL,2021,MIT;installer retains their full LICENSE.
This adapter extracts only three reviewed MIT definitions,provides strict
interface wrappers,and blocks every actual restricted CroCo/RoPE implementation.
It does not relicense,copy or execute the UniCeption CroCo implementation.
"""
import ast
from contextlib import contextmanager
import importlib
import importlib.abc
import importlib.machinery
import importlib.metadata
from pathlib import Path
import sys
import types

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from headfoundry.manifest import sha256_file

ASSET = ROOT/'assets/private/mapanything-apache-0248'
MIT_BLOCK_SHA = '16ce2f53322a7d912ced6057c90bbaf8f2fa12ac1304d4fd6f4c358ff710be6a'


@contextmanager
def meta_parameter_construction():
    """Fresh isolated model only:defer learned storage,keep scalar setup on CPU."""
    import torch
    original = torch.nn.Module.register_parameter

    def register(module, name, parameter):
        if parameter is not None and parameter.device.type != 'meta':
            parameter = torch.nn.Parameter(parameter.detach().to('meta'), requires_grad=parameter.requires_grad)
        return original(module, name, parameter)
    torch.nn.Module.register_parameter = register
    try:
        yield
    finally:
        torch.nn.Module.register_parameter = original


def expand_verified_parameter_aliases(model, state, metadata):
    """Cover every model key,using only publisher aliases of identical parameters."""
    variables = model.state_dict(keep_vars=True)
    if set(state)-set(variables):
        raise ValueError('Unexpected learned tensor keys')
    expanded = dict(state)
    used, aliases = set(), {}
    for key, value in variables.items():
        canonical = key
        seen = set()
        while canonical not in state:
            if canonical in seen or canonical not in metadata:
                raise ValueError('Missing learned tensor or cyclic/undeclared alias:'+key)
            seen.add(canonical)
            canonical = metadata[canonical]
        if key != canonical:
            if canonical not in variables or variables[key] is not variables[canonical]:
                raise ValueError('Header alias does not match actual shared model parameter:'+key)
            aliases[key] = canonical
        tensor = state[canonical]
        if tensor.shape != value.shape or tensor.dtype != value.dtype:
            raise ValueError('Exact learned tensor shape/dtype mismatch:'+key)
        expanded[key] = tensor
        used.add(canonical)
    if used != set(state):
        raise ValueError('An actual checkpoint tensor was not consumed')
    return expanded, aliases


def mit_dpt_definitions(path, expected=MIT_BLOCK_SHA):
    if sha256_file(Path(path)) != expected:
        raise ValueError('Exact reviewed original MIT DPT source required')
    import torch
    from torch import nn
    parsed = ast.parse(Path(path).read_text(encoding='utf-8'))
    selected = {'_make_scratch', 'ResidualConvUnit_custom', 'FeatureFusionBlock_custom'}
    nodes = [n for n in parsed.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in selected]
    if {n.name for n in nodes} != selected or len(nodes) != 3:
        raise ValueError('Unexpected original MIT DPT API')
    namespace = {'torch': torch, 'nn': nn, '__name__': 'headfoundry_original_mit_dpt'}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), 'exec'), namespace)
    return namespace


def make_dpt_provider(path=ASSET/'source/dpt/blocks.py'):
    from torch import nn
    original = mit_dpt_definitions(path)
    provider = types.ModuleType('headfoundry_mit_dpt_provider')
    provider.__file__ = str(Path(path).resolve())
    provider.__headfoundry_license__ = 'MIT-original-Intel-ISL-DPT'

    def make_nonlinearity(name):
        if name != 'relu':
            raise ValueError('Only exact reviewed Apache checkpoint ReLU path is supported')
        return nn.ReLU(inplace=False)

    def make_fusion_block(features, use_bn=False, output_width_ratio=1, nonlinearity='relu'):
        if use_bn or output_width_ratio != 1:
            raise ValueError('Unreviewed DPT architecture variant refused')
        return original['FeatureFusionBlock_custom'](features, make_nonlinearity(nonlinearity),
            bn=False, expand=False, align_corners=True)

    provider.make_fusion_block = make_fusion_block
    def make_scratch(in_shape, out_shape, groups=1, expand=False):
        scratch = original['_make_scratch'](in_shape, out_shape, groups=groups, expand=expand)
        # The BSD wrapper expects a list AND the original named aliases. These
        # are the same MIT convolution objects,not extra/random learned layers.
        scratch.layer_rn = nn.ModuleList([getattr(scratch, f'layer{i}_rn') for i in range(1, 5)])
        return scratch
    provider.make_scratch = make_scratch
    provider.make_nonlinearity = make_nonlinearity
    provider.pair = lambda value: value if isinstance(value, tuple) else (value, value)
    return provider


class RestrictedComponentImportGuard(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if (fullname.startswith('uniception.models.libs.croco')
                or fullname.split('.')[0] in ('dust3r', 'mast3r', 'pi3', 'vggt')):
            raise PermissionError('Restricted/unreviewed model implementation blocked: '+fullname)
        return None


def install_permissive_runtime():
    import torch
    if importlib.metadata.version('uniception') != '0.1.7':
        raise ValueError('Reviewed UniCeption0.1.7 required')
    if any(n.startswith('uniception.models.encoders') or n.startswith('uniception.models.libs.croco') for n in sys.modules):
        raise RuntimeError('Start a clean process;never replace an already imported restricted component')
    provider = make_dpt_provider()
    parent = types.ModuleType('uniception.models.libs.croco')
    parent.__path__ = []
    parent.__spec__ = importlib.machinery.ModuleSpec(parent.__name__, loader=None, is_package=True)
    parent.__file__ = __file__
    parent.__headfoundry_license__ = 'Independent fail-closed namespace adapter'
    provider.__name__ = parent.__name__+'.dpt_block'
    positional = types.ModuleType(parent.__name__+'.pos_embed')
    positional.__file__ = __file__

    class DisabledRoPE:
        def __init__(self, *args, **kwargs):
            raise PermissionError('Restricted RoPE is unsupported,not approximated or silently replaced')
    positional.RoPE2D = DisabledRoPE
    sys.modules[parent.__name__] = parent
    sys.modules[provider.__name__] = provider
    sys.modules[positional.__name__] = positional
    sys.meta_path.insert(0, RestrictedComponentImportGuard())
    # Explicit three-encoder facade avoids the upstream eager optional CroCo,
    # Cosmos and other unrelated encoder imports;their implementations stay idle.
    package = Path(importlib.metadata.distribution('uniception').locate_file('uniception'))
    facade = types.ModuleType('uniception.models.encoders')
    facade.__path__ = [str(package/'models/encoders')]
    facade.__spec__ = importlib.machinery.ModuleSpec(facade.__name__, loader=None, is_package=True)
    facade.__file__ = __file__
    sys.modules[facade.__name__] = facade
    base = importlib.import_module(facade.__name__+'.base')
    for name in dir(base):
        if not name.startswith('_'):
            setattr(facade, name, getattr(base, name))
    dino = importlib.import_module(facade.__name__+'.dinov2')
    dense = importlib.import_module(facade.__name__+'.dense_rep_encoder')
    glob = importlib.import_module(facade.__name__+'.global_rep_encoder')
    classes = {'dinov2': dino.DINOv2Encoder, 'dense_rep_encoder': dense.DenseRepresentationEncoder,
        'global_rep_encoder': glob.GlobalRepresentationEncoder}

    def encoder_factory(encoder_str, **kwargs):
        if encoder_str not in classes:
            raise PermissionError('Only reviewed Apache model encoders may execute')
        return classes[encoder_str](**kwargs)

    def feature_returner_encoder_factory(encoder_str, **kwargs):
        if encoder_str != 'dinov2':
            raise PermissionError('Unreviewed feature encoder refused')
        return dino.DINOv2IntermediateFeatureReturner(**kwargs)
    facade.encoder_factory = encoder_factory
    facade.feature_returner_encoder_factory = feature_returner_encoder_factory
    facade.get_available_encoders = lambda: list(classes)
    old_hub_load = torch.hub.load
    calls = []

    def local_dino_only(repository, model, *args, **kwargs):
        if (repository != 'facebookresearch/dinov2' or model != 'dinov2_vitg14'
                or kwargs.get('pretrained') is not False or args):
            raise PermissionError('Unreviewed architecture/encoder weight download refused')
        calls.append({'model': model, 'pretrained': False, 'source': 'local pinned DINOv2'})
        return old_hub_load(str(ASSET/'source/dinov2'), model, source='local', pretrained=False)
    torch.hub.load = local_dino_only
    return {'provider': provider, 'dino_calls': calls, 'facade': facade}


def audit_imported_provenance():
    allowed_proxies = {'uniception.models.libs.croco', 'uniception.models.libs.croco.dpt_block',
        'uniception.models.libs.croco.pos_embed'}
    result = {}
    for name, module in list(sys.modules.items()):
        filename = getattr(module, '__file__', None)
        if name.startswith('uniception.models.libs.croco'):
            if name not in allowed_proxies or not filename or '/libs/croco/' in str(filename).replace('\\', '/'):
                raise PermissionError('Actual noncommercial implementation entered process')
        if name.startswith(('mapanything', 'uniception', 'dinov2', 'headfoundry_original_mit_dpt')) and filename:
            result[name] = {'path': str(filename), 'sha256': sha256_file(Path(filename))}
    return result
