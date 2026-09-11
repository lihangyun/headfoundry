# Experiment 0089: nasal/lip fit on the coupled configuration

Status: `UNVERIFIED`; no promotion. Left profile regresses slightly.

Use experiment 0079's pinned joint head and cameras as an explicitly unaccepted
starting configuration. Fit the same ten signed CC0 nasal/lip controls from
0083, with the same profile rows, detector observations, supplied scales and
coefficient limits. Cameras stay fixed during this solve. This tests the
configuration suggested by 0088; differences from 0083 include both the starting
nasal shape and cameras, so do not attribute all cross-experiment gains to pose.

All three starts converge in 41/68/79 evaluations, costs
30.853026/30.793948/30.922154. The best candidate has no reversed triangles or
lost eligible ray-visible samples. Maximum displacement from its immediate
source is 0.010326 template units. Minimum area ratio is 0.829236 against that
source, but only 0.560725 against the original neck-cut head. Both references
are checked on the exported OBJ; incremental quality alone must not conceal
accumulated deformation.

| Fitting diagnostic px | Immediate coupled source | Candidate |
| --- | ---: | ---: |
| Left local profile MAE | 3.4610 | 3.4900 |
| Right local profile MAE | 7.0696 | 6.8624 |
| Left whole profile MAE | 3.5891 | 3.6216 |
| Right whole profile MAE | 7.2493 | 7.0714 |
| Front point mean | 5.0944 | 4.2430 |
| Left-oblique point mean | 7.2815 | 6.6219 |
| Right-oblique point mean | 5.9916 | 5.3568 |

Render actual five-view comparisons against both the original neck-cut head
with original cameras and the immediate coupled head with its own cameras.
The immediate-source comparison was visually inspected: nose/lip changes are
small, generic facial anatomy and the unresolved lip seam remain. The right
profile gain and point-error reductions do not establish bilateral improvement
or recognizable identity. All observations are fitting data; camera acceptance
remains failed and these renders are not a licensed competitive benchmark.

Private `coupled-nasolabial-v1` contains actual OBJ, matching cameras, fit report,
both comparison sheets and both exported-mesh audits. No personal data is
committed. Existing asset locks and local consent are checked before fitting.
Public production code remains unchanged. Validation was the real three-start
fit, ray visibility and independent exported mesh/render checks.

Next requires a configuration-aware lip-seam treatment with cross-view
uncertainty, rather than another identical ten-control sweep. Preserve the
original source reference when measuring accumulated mesh degradation.
