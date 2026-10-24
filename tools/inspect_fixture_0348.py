"""Read owned fixture schemas before freezing a prediction protocol."""
from pathlib import Path
import numpy as np

root = Path(__file__).resolve().parents[1] / 'assets/private/dense-photo-0332'
for name in ('truth.npz', 'observations.npz', 'endpoint-truth.npz'):
    with np.load(root / name, allow_pickle=False) as data:
        print(name, {key: {'shape': data[key].shape, 'dtype': str(data[key].dtype)} for key in data.files})
