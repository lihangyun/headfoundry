import struct
import tempfile
import unittest
from pathlib import Path

import numpy as np

from headfoundry.scan import read_binary_stl


class BinaryScanTests(unittest.TestCase):
    def test_exact_coordinates_order_and_corrupt_input(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "scan.stl"
            # Shared vertices remain shared; no tolerance welding of near points.
            triangles = [(0., 0., 0., 1., 0., 0., 0., 1., 0.),
                         (0., 1., 0., 1., 0., 0., 1e-7, 0., 0.)]
            payload = b" " * 80 + struct.pack("<I", 2)
            for values in triangles:
                payload += struct.pack("<12fH", 0., 0., 1., *values, 0)
            path.write_bytes(payload)
            vertices, faces = read_binary_stl(path)
            self.assertEqual(len(vertices), 4)
            np.testing.assert_allclose(vertices[faces], np.array(triangles).reshape(2, 3, 3), rtol=1e-7)
            for broken in (payload[:40], payload[:-1], payload + b"x",
                           payload[:96] + struct.pack("<f", float("nan")) + payload[100:]):
                path.write_bytes(broken)
                with self.assertRaises(ValueError):
                    read_binary_stl(path)


if __name__ == "__main__":
    unittest.main()
