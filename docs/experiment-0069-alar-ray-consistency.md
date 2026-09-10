# Experiment 0069: alar two-view ray consistency

Status: `UNVERIFIED` diagnostic; no new mesh or accepted camera.

Following 0068, test whether visible nasal observations can be explained by
free 3D points at all under the supplied cameras, instead of blaming only
the authored shape basis. Pair front with left30 for IDs 98/129/64 and
front with right30 for 327/358/294. Use only previously inspected near-side
observations. Initialize with the existing linear triangulator, then refine
each point using two-view pixel least squares; mesh geometry is not a prior.
All point solves converge with positive camera depth.

Evaluate original cameras and the unaccepted canthus/contour cameras from
0065. A 32-sample perturbation probe adds independent Gaussian 3px noise to
the two image observations, using identical per-ID random samples for the
two camera variants. This is a sensitivity assumption, not a measured noise
model or statistical confidence interval. No thresholds are loosened.

| ID | Original-camera worst-view residual px | Candidate-camera residual px | Original point distance from source | Original 3px perturbation spread p95 |
| --- | ---: | ---: | ---: | ---: |
| 98 | 4.5226 | 4.0427 | 0.01596 | 0.02767 |
| 129 | 4.4073 | 4.0748 | 0.01491 | 0.03114 |
| 64 | 5.1271 | 4.6339 | 0.03625 | 0.03110 |
| 327 | 2.8922 | 2.0907 | 0.01662 | 0.04698 |
| 358 | 2.9847 | 2.3980 | 0.02250 | 0.03098 |
| 294 | 3.4413 | 2.6442 | 0.02568 | 0.04294 |

Distances/spreads are template units, not millimetres. Even freely positioned
points leave several-pixel disagreement. Thus stronger deformation cannot
fully reconcile these pairs at these cameras. The candidate cameras reduce
some residuals but are not independently calibrated. This does not isolate
camera error from anatomical correspondence or detector error.

Most recovered point offsets are smaller than this assumed perturbation
spread; do not treat the triangulated positions as exact geometry targets.
This supports uncertainty-aware fitting and better observed feature support,
not a claim that all residual shape error is noise. Preserve photo reading,
camera uncertainty and topology correspondence as separate questions.

Private `alar-triangulation-v2` stores the per-point coordinates, original
support positions, differences, depth, residuals and matched-seed sensitivity
probe. v1 used unmatched random draws between camera variants and is not
used for comparative spread conclusions. The local runner checks photo
consent and source/support hashes and records camera hashes. Existing
triangulation and SciPy are reused; no external data transfer occurs. All
72 tests pass. Original meshes/cameras remain untouched.

Next incorporate explicit observation uncertainty in the experimental fitting
objective and test whether it avoids chasing these several-pixel conflicts,
without claiming better likeness from ignored residuals. Acceptance still
requires actual visual improvement and independent evidence.
