"""Exact binary STL import for local scan diagnostics; units remain unknown."""
from pathlib import Path
import struct

import numpy as np


def read_binary_stl(path):
    """Preserve triangle order; weld only exactly equal numeric coordinates.

    No repair, normal recalculation, axis change or unit inference is performed.
    ASCII STL is deliberately unsupported by this small intake path.
    """
    path = Path(path)
    with path.open("rb") as stream:
        header = stream.read(84)
        if len(header) != 84:
            raise ValueError("Truncated binary STL header")
        count = struct.unpack_from("<I", header, 80)[0]
        if not count or path.stat().st_size != 84 + 50 * count:
            raise ValueError("Binary STL size/count mismatch or empty mesh")
        dtype = np.dtype([("normal", "<f4", (3,)), ("vertices", "<f4", (3, 3)),
                          ("attribute", "<u2")])
        triangles = np.fromfile(stream, dtype=dtype, count=count)
    if len(triangles) != count or not np.isfinite(triangles["vertices"]).all():
        raise ValueError("Incomplete or nonfinite STL positions")
    vertices, inverse = np.unique(triangles["vertices"].reshape(-1, 3), axis=0, return_inverse=True)
    return vertices.astype(float), inverse.reshape(-1, 3)
