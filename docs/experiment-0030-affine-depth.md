# Experiment 0030: bounded affine depth correction

Status: `REJECT`; negligible held improvement, no usable head produced.

The optional depth-offset mode extends each non-reference camera's depth rule
from z'=s*z to z'=s*z+b. Offsets move points along their original camera rays,
not a constant world translation. The reference camera/scale/offset remain fixed.
Offset limits are +/-0.1 input units, tightened where necessary to preserve
positive training depths even at the minimum allowed scale. This safeguard
does not validate all unsampled dense depths; no dense output is published.
Other bounds, weights, observations and held split remain unchanged.

Private command: `fit_depth_cameras.py --pixels --offset --output
depth-camera-offset-v1`. Convergence: 17 evaluations. Fitted offsets:
0, -0.0014346743, -0.0075778031. right30 rx remains at -0.1 rad.

| Held diagnostic | Scale only | Scale + offset |
| --- | ---: | ---: |
| Track projection p95, px | 8.8242 | 8.6986 |
| Frozen manual projection p95, px | 14.3528 | 14.1752 |
| Depth disagreement p95, input units | 0.006136 | 0.006150 |

These small differences do not resolve the active-bound conflict or meet the
3 px gate. Depth disagreement slightly worsens. No geometry, default mode or
acceptance baseline was replaced. The optional flexibility is tested but not
promoted to a production path.

52 tests pass, including recovery of known depth scale and offset alongside
camera registration. Offset mode defaults off. This is bounded engineering
evidence, not proof of dense shape correctness.

Next stage should test an explicit shared experimental head surface constrained
by consented photo landmarks and silhouettes, with uncertain/unseen regions
identified. The user has authorized experimental geometry before camera
acceptance. Preserve camera uncertainty and independent visual comparison;
do not call a template or fitted outline a verified full likeness.
