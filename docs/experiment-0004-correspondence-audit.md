# Experiment 0004: recheck the failed camera initializer

Status: UNVERIFIED. No real camera or full head has passed acceptance.

The previous COLMAP run found no verified image pairs. This establishes failure
of that run, not that the photographs are unsuitable or synthetic. No evidence
establishes how the photographs were produced.

On 2026-09-05, a read-only audit reused the stored SIFT descriptors and keypoints.
The sole variable was correspondence matching/verification: OpenCV L2 matching,
0.8 ratio test, and USAC_MAGSAC fundamental matrix estimation at 2 pixels.
Across ten pairs it found 14–66 ratio candidates and 8–19 epipolar inliers.
These counts are weak evidence: a fundamental matrix can fit spurious or
degenerate correspondences, especially at low support. They are not a camera gate.

Reproduce with the local environment:

```powershell
.venv\Scripts\python.exe tools\audit_colmap_matches.py <private-database.db>
```

The database opens read-only. Originals, crops, masks, camera assumptions, and
all existing reconstruction outputs remain unchanged. Identity-specific data
stays under the ignored private asset directory.

Next experiment: explicitly annotated anatomical correspondences and camera
optimization. Profile silhouettes must be treated as view-dependent contours,
not identical surface points across photographs. Reserve observations for
validation; do not assess camera accuracy only on fitted points. Keep full-head
geometry and texture acceptance separate from the camera result.
