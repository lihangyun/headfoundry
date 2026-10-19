from pathlib import Path
import hashlib
import sys
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'tools')]
from mapanything_permissive_runtime_0248 import meta_parameter_construction, mit_dpt_definitions, expand_verified_parameter_aliases


class PermissiveRuntimeTests(unittest.TestCase):
    def test_meta_construction_strict_assign_preserves_full_float32_parameters(self):
        import torch
        original = torch.nn.Module.register_parameter
        reference = torch.nn.Sequential(torch.nn.Linear(4, 7), torch.nn.ReLU(), torch.nn.Linear(7, 2))
        with meta_parameter_construction():
            model = torch.nn.Sequential(torch.nn.Linear(4, 7), torch.nn.ReLU(), torch.nn.Linear(7, 2))
            self.assertTrue(all(p.device.type == 'meta' for p in model.parameters()))
        self.assertIs(torch.nn.Module.register_parameter, original)
        result = model.load_state_dict(reference.state_dict(), strict=True, assign=True)
        self.assertFalse(result.missing_keys or result.unexpected_keys)
        self.assertTrue(all(p.device.type == 'cpu' and p.dtype == torch.float32 for p in model.parameters()))
        data = torch.arange(12, dtype=torch.float32).reshape(3, 4)
        torch.testing.assert_close(model(data), reference(data), rtol=0, atol=0)

    def test_only_pinned_mit_definitions_execute_not_top_level_backbone_import(self):
        source = "raise RuntimeError('unrelated top level must not execute')\ndef _make_scratch(): pass\nclass ResidualConvUnit_custom: pass\nclass FeatureFusionBlock_custom: pass\n"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'original.py'
            path.write_bytes(source.encode('utf-8'))
            namespace = mit_dpt_definitions(path, hashlib.sha256(source.encode()).hexdigest())
            self.assertIn('FeatureFusionBlock_custom', namespace)
            with self.assertRaises(ValueError):
                mit_dpt_definitions(path)

    def test_publisher_alias_must_be_actual_shared_parameter_not_similar_shape(self):
        import torch
        class Shared(torch.nn.Module):
            def __init__(self, tied):
                super().__init__()
                self.left = torch.nn.Linear(3, 2)
                self.right = self.left if tied else torch.nn.Linear(3, 2)
        reference = Shared(True)
        state = {k: v for k, v in reference.state_dict().items() if k.startswith('left.')}
        metadata = {'right.weight': 'left.weight', 'right.bias': 'left.bias'}
        with meta_parameter_construction():
            model = Shared(True)
        expanded, aliases = expand_verified_parameter_aliases(model, state, metadata)
        model.load_state_dict(expanded, strict=True, assign=True)
        self.assertEqual(len(aliases), 2)
        self.assertIs(model.left, model.right)
        with self.assertRaises(ValueError):
            expand_verified_parameter_aliases(Shared(False), state, metadata)
        with self.assertRaises(ValueError):
            expand_verified_parameter_aliases(reference, state, {})
