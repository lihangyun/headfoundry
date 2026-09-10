# Experiment 0062: pose after explicit anchor rejection

Status: `REJECT` for camera promotion. No accepted source changes.

Execute the previously pending experiment from 0061: exclude left30 mouth
anchor 5, right30 mouth anchor 4 and right90 nose anchor 6. Keep geometry,
1800px intrinsics, remaining observations, initial cameras, robust loss and
bounds identical to the 1800px refit in 0060. Only the fitting mask changes.
The local runner's explicit `--screened` option writes to a new exclusive
directory and leaves its original sweep/default intact. Input consent and
source/camera hash checks remain required. No new coordinates are invented.

The original five masks contain 8/8/5/8/5 points; the new masks contain
8/7/5/7/4. All five solves pass the existing minimum-count/noncoplanarity
checks and converge without active bounds. Entire-mesh depth stays positive.
Those technical checks are not evidence that the remaining points identify
the correct camera.

| Regression diagnostic, px MAE | Original cameras | All-point refit | Screened refit |
| --- | ---: | ---: | ---: |
| Left profile | 3.6420 | 4.4372 | 4.4372 |
| Right profile | 8.0322 | 12.3758 | 17.3383 |

On the same retained four right-profile anchors, mean error decreases from
14.1399px (original camera) to 11.1127px (screened camera). Evaluating on the
original five-point mask instead gives 15.8490px to 16.8039px. Both masks and
both metrics are retained; deleting observations must not masquerade as a
same-support improvement. Profiles were excluded from this solve but used
in source construction and remain regression checks, not fresh ground truth.

The actual bilateral photo/original/all-point/screened comparison was inspected.
The screened right pose visibly turns away from the supplied profile and
changes projected scale. Thus point removal is necessary data hygiene, but
does not repair the camera objective: sparse, still-uncertain eye/chin/mouth
correspondences permit a worse pose even though the solver is numerically
successful. Do not restore the invalid nose observation just because it
previously constrained pose, or relax support requirements to force a result.

Private `screened-anchor-pose-v1` retains camera arrays, complete residuals,
masks, solver diagnostics and the actual comparison. The reusable private
renderer accepts `--screened` without altering the prior focal outputs.
All 72 existing tests pass; original mesh/registration files stay untouched.
Next introduce verified side-view anatomical/contour support with explicit
semantics and visibility, rather than repeating these four-point rigid fits.
Camera and complete visual reconstruction acceptance remain unmet.
