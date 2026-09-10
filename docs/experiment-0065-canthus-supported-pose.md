# Experiment 0065: pose with visible canthus candidates

Status: `UNVERIFIED`; original model and cameras are not replaced.

Use the four candidate vertex identities from 0064 with the screened-anchor
and profile-arc protocol of 0063. Geometry, intrinsics, original pose seeds,
mask, loss, bounds and contour support remain identical. Only four eye-point
identities change. Verify candidate source/camera provenance before use.
All required canthi pass the 1e-5-unit nearest-surface visibility check in
their originally eligible views before solving. This includes the near eye
in each profile. Far eyes remain explicitly excluded; do not make them
eligible just because their projected coordinates exist.

All five pose solves converge without active bounds, and all used canthi
remain visible afterwards (largest gap below 1e-12 template units). Entire
mesh depth stays positive. The two excluded far-eye gaps on each profile
remain substantial, approximately 0.28–0.57 units. This agrees with the mask,
not with using every vertex projection as an observed point.

To avoid mistaking a correspondence change for improved pose, evaluate both
the previous 0063 cameras and the new cameras on the same candidate support:

| Retained-anchor mean px | Previous pose, candidate support | New pose, candidate support |
| --- | ---: | ---: |
| Front | 4.1540 | 4.1542 |
| Left30 | 6.5100 | 6.4972 |
| Left profile | 10.0462 | 9.9720 |
| Right30 | 7.1693 | 7.1029 |
| Right profile | 15.9750 | 16.0042 |

Actual-envelope profile MAE changes from 2.7445/4.7013px in 0063 to
2.7532/4.6827px here. Differences are tiny and not uniformly favorable.
Most apparent anchor gains versus old published numbers come from changing
the correspondence itself, not discovering a substantially better camera.
Both profiles and anchors are fitting inputs, not independent validation.

Actual bilateral photo/original/old-canthus/new-canthus renders were inspected.
The last two are visually almost unchanged, with generic nose and lips still
present. No new likeness or camera-quality claim is supported. Preserve the
visible canthus candidates for controlled future work, but do not promote
this pose as an accepted calibration or repeat this small eye-only change
expecting a different facial reconstruction.

Private `canthus-contour-pose-v1` retains candidate provenance, masks,
before/after visibility, same-support comparison, camera arrays and native
render sheet. The private runner/renderer use explicit `--canthus` and leave
all prior outputs intact. All 72 tests pass. Next address nasal/labial shape
support and its cross-view observations rather than further canthus-only
pose micro-adjustment; whole-product acceptance is still far from established.
