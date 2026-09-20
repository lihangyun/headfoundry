# Experiment 0127: explicit view-mean protection

Continue 0126 on the same reconnected source mesh. Test SLSQP with explicit
non-regression inequalities for both oblique four-eye means and both corrected
profile means. Keep the same nine parameters, bounds, priors, targets and
actual surface supports. Start at zero displacement/rotation. Geometry guards
remain post-fit checks. This tests constrained solving, not new observations.

The saved solve reports `success: false`. Its left-eye constraint is violated
by 0.000967968 px; the other three constraint slacks are positive. Do not round
this to feasibility or treat the exported diagnostic OBJ as a successful fit.
The solver message was not persisted, so its termination cause is unverified;
do not label it an iteration-limit failure without further evidence.

| Metric | Source left/right px | Candidate left/right px |
| --- | --- | --- |
| Four-eye mean | 5.471895 / 4.847883 | 5.472863 / 4.272943 |
| Profile mean | 4.574355 / 6.176893 | 4.470330 / 6.078118 |

Minimum triangle area ratio is 0.883594, relative normal reversals zero and
maximum displacement 0.007233 template units. Numerical mesh stability remains
better than the old connectivity, but that does not cure fit failure.

An additional limitation is exposed by per-point evidence: left-oblique eye
ID 263 worsens from 5.4212 to 10.2960 px while other eyes compensate in the
mean. Even a converged view-mean-constrained solution would not establish
per-anchor protection. Preserve every row; do not hide that local regression.

Candidate promotion is `REJECT`. Private `shared-surface-protected-v1` retains
the failed solver's OBJ, cameras, constraint slacks and full point errors.
No default, camera gate or acceptance tolerance changes. A future protected
solve needs per-anchor safeguards and a persisted termination reason, plus
actual visual evidence; simply relaxing feasibility tolerance is not a fix.

On quota recovery, the completed local solver artifacts were found with no
matching live process; the solve was not restarted. Five-view rendering was
completed and inspected: the flat lower lip and generic identity persist.
This adds no visual basis for promotion. All 99 public tests and
`git diff --check` pass; public implementation remains unchanged.
