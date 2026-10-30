"""Neutral-pose FLAME expression blendshapes with separately locked provenance.

Jaw/neck rotations and pose correctives are not implemented here. Callers must
check final geometry/contact; bounded coefficients do not guarantee safe meshes.
"""
import json
from dataclasses import dataclass
from pathlib import Path
import numpy as np
from .flame import FlameIdentityModel
from .manifest import sha256_file

CONVERSION_ID = 'numpy-neutral-pose-expression-v1'


@dataclass(frozen=True)
class FlameExpressionModel:
    identity: FlameIdentityModel
    expression_directions: np.ndarray

    @classmethod
    def from_lock(cls, path):
        path = Path(path)
        record = json.loads(path.read_text(encoding='utf8'))
        if record.get('conversion_id') != CONVERSION_ID or record.get('expression_components') != 'last_100':
            raise ValueError('Unsupported expression conversion')
        identity_lock = path.parent / record['identity_lock']
        if sha256_file(identity_lock) != record['identity_lock_sha256']:
            raise ValueError('Identity provenance changed')
        original = json.loads(identity_lock.read_text(encoding='utf8'))
        identity = FlameIdentityModel.from_asset_record(original, identity_lock.parent)
        if record.get('source_model_sha256') != original['model_sha256']:
            raise ValueError('Expression/identity source mismatch')
        asset = path.parent / record['path']
        if sha256_file(asset) != record['sha256']:
            raise ValueError('Expression asset hash mismatch')
        directions = np.load(asset, allow_pickle=False)
        model = cls(identity, directions)
        model.validate()
        return model

    def validate(self):
        self.identity.validate()
        if (self.expression_directions.shape != (*self.identity.template.shape,100)
                or not np.isfinite(self.expression_directions).all()):
            raise ValueError('100 finite expression directions matching identity topology required')

    def vertices(self, identity, expression, max_absolute=3.):
        self.validate()
        expression = np.asarray(expression, float)
        if (expression.shape != (100,) or not np.isfinite(expression).all()
                or not np.isfinite(max_absolute) or max_absolute <= 0
                or (np.abs(expression) > max_absolute).any()):
            raise ValueError('Finite bounded 100-component expression required')
        neutral = self.identity.neutral_vertices(identity, max_absolute)
        return neutral + np.einsum('vck,k->vc', self.expression_directions, expression)
