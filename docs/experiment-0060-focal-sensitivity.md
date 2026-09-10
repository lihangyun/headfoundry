# Experiment 0060: fixed-shape focal sensitivity

Status: `REJECT` for camera promotion. Original mesh and cameras unchanged.

Prior shape experiments did not resolve central facial likeness. Test whether
the assumed 1800px focal is driving those defects before adding further shape
parameters. Keep oblique-jaw-v3 geometry, principal point and eight template
anchor identities fixed. Sweep a shared focal of 1200, 1800, 2400 and 3600px
on the original 1254px square photos; these are pixel focal lengths, not EXIF
millimetres. Refit each view's rigid pose using its existing visible anchor
mask, robust soft-L1 loss and 5px scale. Initialize camera depth in proportion
to focal, allow rotation +/-0.35 radians, x/y translation +/-0.5 and depth
+/-35 percent. All 20 solves converge without active bounds and with positive
depth for the entire mesh. No geometry fitting, principal-point fitting or
lens-distortion model is introduced.

Verify photo consent and source/camera hashes before the private run. The two
profile curves are excluded from this solve but were used earlier in mesh
construction: regression evidence, not new independent calibration truth.

| Camera setting | Left profile MAE px | Right profile MAE px |
| --- | ---: | ---: |
| Original fixed 1800px cameras | 3.6420 | 8.0322 |
| Refit at 1200px | 3.7881 | 16.1459 |
| Refit at 1800px | 4.4372 | 12.3758 |
| Refit at 2400px | 5.1411 | 11.3023 |
| Refit at 3600px | 5.8631 | 10.2382 |

At 3600px, mean training anchor errors by view are 4.9041, 7.0877, 10.0578,
8.0191 and 15.3295px, compared with original 5.2854, 7.1458, 9.9285, 8.1446
and 15.8490px. Some training improvements coexist with worse profiles. The
1200px right chin endpoint has a 61.1453px horizontal residual; retain it,
including the risk of an outer-envelope branch switch, rather than trimming
it from the report. Other focal candidates also fail the bilateral comparison.

Actual photo/original/four-candidate bilateral clay views were inspected.
Changing perspective has visible effects but does not establish better
subject likeness. In particular, even same-focal pose refitting regresses
the profile: the anchor-only objective is not consistent with the existing
profile-fitted source. This does not identify which component is correct.
Template anchor semantics, detector reading, source shape and camera are
still coupled; it is not proof that 1800px is the true focal or that another
camera model cannot work. Do not choose 3600px merely for smaller anchor loss.

Private `focal-sensitivity-v1` retains all camera arrays, full residuals,
solver records and the actual comparison. The local runner and renderer
remain outside Git with subject data. All 72 existing tests pass. Next audit
the anatomical correspondence of the eight source anchors against visible
photo features before stronger pose or central-face deformation. Repeating
an anchor-only focal sweep with the same ambiguous correspondences is not
supported by this result.
