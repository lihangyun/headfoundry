# Experiment 0135: dense profile camera split

## Question

Can the two profile cameras be refined on the unchanged experiment-0132 mesh
using dense contour rows that were not direct sparse fitting samples? Intrinsics,
camera centers, all other cameras and the mesh stay fixed. Fit only two bounded
rotation vectors to even dense rows; reserve odd rows for audit. Then line-scan
the solved direction while requiring both legacy sparse profile means to be no
worse.

## Result

The free solve improves dense rows but regresses the legacy sparse samples. A
101-step exact line scan retains 76% of that direction, where both evidence sets
improve:

| Diagnostic | Experiment 0132 cameras | Protected camera |
| --- | ---: | ---: |
| Sparse left/right mean | 3.623644 / 4.923310 px | 3.619208 / 4.900249 px |
| Dense selection mean | 5.847073 / 4.610125 px | 5.410515 / 4.032963 px |
| Dense audit mean | 5.712704 / 4.762039 px | 5.256264 / 4.169901 px |
| Dense audit p95 | 13.616793 / 16.339590 px | 12.299536 / 13.311627 px |

Rotation matrices remain orthonormal with determinant one; camera centers and
the 1800 px focal values are unchanged, and all mesh depths stay positive. The
actual profile overlay shows a real but small pose/roll correction rather than
a visible identity change. Hair/scalp and neck movement cannot validate facial
camera accuracy.

The deterministic fit, split and physical matrix checks are
`TECHNICAL_CHECK_PASSED`. The camera is `PARTIAL_SUCCESS` as a nonzero transfer
result and `REJECT` for promotion: both row sets originate from the same trace,
the source mesh already used related sparse observations, and no independent
calibration target or EXIF focal metadata exists. The global camera gate remains
failed.
