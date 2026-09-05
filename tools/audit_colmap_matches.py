"""Read an existing COLMAP database without changing its reconstruction.

Candidate matches and epipolar inliers are diagnostics, not accepted cameras.
Requires the optional locally installed NumPy and OpenCV packages.
"""
import argparse
import json
import sqlite3
from pathlib import Path

import cv2
import numpy as np


def audit(path: Path) -> dict:
    with sqlite3.connect(path.resolve().as_uri() + '?mode=ro', uri=True) as db:
        names = dict(db.execute('SELECT image_id,name FROM images'))
        descriptors = {
            i: np.frombuffer(data, np.uint8).reshape(rows, cols).astype(np.float32)
            for i, rows, cols, data in db.execute('SELECT image_id,rows,cols,data FROM descriptors')
        }
        points = {
            i: np.frombuffer(data, np.float32).reshape(rows, cols)[:, :2]
            for i, rows, cols, data in db.execute('SELECT image_id,rows,cols,data FROM keypoints')
        }
        original = [int(row[0]) for row in db.execute('SELECT rows FROM two_view_geometries')]
    cv2.setRNGSeed(20260905)
    matcher = cv2.BFMatcher(cv2.NORM_L2)
    pairs = []
    for i in sorted(descriptors):
        for j in sorted(descriptors):
            if i >= j:
                continue
            matches = matcher.knnMatch(descriptors[i], descriptors[j], k=2)
            good = [(pair[0].queryIdx, pair[0].trainIdx) for pair in matches
                    if len(pair) == 2 and pair[0].distance < .8 * pair[1].distance]
            count = 0
            if len(good) >= 8:
                indices = np.asarray(good)
                _, mask = cv2.findFundamentalMat(
                    points[i][indices[:, 0]], points[j][indices[:, 1]],
                    cv2.USAC_MAGSAC, 2., .999, 10000)
                count = int(mask.sum()) if mask is not None else 0
            pairs.append({'images': [names[i], names[j]],
                          'ratio_candidates': len(good), 'epipolar_inliers': count})
    return {'status': 'UNVERIFIED', 'opencv_version': cv2.__version__,
            'colmap_verified_counts': original, 'pairs': pairs,
            'interpretation': 'Sparse matches do not establish physical correspondence, '
            'valid cameras, or photo unsuitability. Review locations and recover cameras next.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('database', type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.database), indent=2))
