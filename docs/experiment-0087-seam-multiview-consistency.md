# Experiment 0087: seam consistency without mesh constraints

Status: `UNVERIFIED`; no camera, support or geometry promotion.

Fit samples 13 and 14 as two independent free 3D points using all three
front/oblique detector observations and the unchanged original cameras.
This removes mesh topology, lip configuration and graphical-basis limitations
from the solve. Check convergence and positive camera depth. Separately fit
one shared point to all six observations to test the closed-seam hypothesis.

| Sample | Front error px | Left oblique error px | Right oblique error px |
| --- | ---: | ---: | ---: |
| Independent 13 | 5.6948 | 5.1095 | 0.9998 |
| Independent 14 | 6.0099 | 5.3305 | 1.1239 |
| Shared point against 13 | 5.5628 | 5.2321 | 1.1691 |
| Shared point against 14 | 6.1493 | 5.2173 | 0.9546 |

Allowing independent points does not resolve the several-pixel disagreement.
The shared point has a similar residual pattern, so simply closing the mouth
cannot be expected to reconcile these fixed-camera observations. This is
evidence of an observation/camera inconsistency, not proof of which view or
detector label is wrong, nor a global-optimum certificate.

Leave one view out of each free-point fit: frontal predictions miss by
8.9338/9.4272 px, left-oblique predictions by 7.7397/8.0524 px and right-oblique
predictions by 1.9469/2.2032 px for samples 13/14 respectively. These are
diagnostics on previously used observations, not newly held-out acceptance
data. Training pairs themselves retain nonzero residuals.

Decision: do not force lip closure or more shape freedom to absorb this
disagreement. The next experiment must address shared cross-view alignment
using actual head constraints and independent facial regions, with profile
protection, rather than optimizing these seam points as exact geometry truth.
Existing images, mesh, cameras and observations remain unchanged. Private
`seam-multiview-v1` records all point fits and leave-one-view errors. Checks:
actual converged point solves, positive depth and recorded camera hash/local
input consent. No public production code or acceptance threshold changed.
