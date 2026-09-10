# Experiment 0064: visible local canthus support

Status: `UNVERIFIED` correspondence candidates, not reconstruction acceptance.
Geometry, cameras and original registration are unchanged.

The anchor audit in 0061 found recessed outer-eye vertices. Search only two
topological rings around each of the four original canthus vertices (19
candidates each). Project each candidate with the original fixed cameras in
front/left30/right30. Require the nearest ray surface to coincide within
1e-5 template units in all three views, then select minimum summed squared
projection distance to the existing manual eye-corner readings. This is
fitting to known observations, not held-out anatomical verification.

| Anchor | Original vertex | Candidate vertex | Visible candidates | Position separation |
| --- | ---: | ---: | ---: | ---: |
| Outer A | 2285 | 1493 | 7 | 0.007192 |
| Inner A | 2268 | 72 | 10 | 0.008253 |
| Inner B | 4439 | 2360 | 10 | 0.008253 |
| Outer B | 4456 | 3685 | 7 | 0.007192 |

Position separation is in template units; no vertex was displaced. The
outer candidates remove the prior ~0.0053/0.0056-unit nearest-surface gap in
one oblique view. Candidate gaps in all three views are at floating-point
noise scale. All twelve per-view fitting errors decrease:

| Anchor | Original errors front/left30/right30 px | Candidate errors px |
| --- | --- | --- |
| Outer A | 6.461 / 3.899 / 9.088 | 4.302 / 3.235 / 8.111 |
| Inner A | 2.827 / 4.783 / 6.526 | 0.776 / 2.044 / 3.700 |
| Inner B | 3.092 / 3.911 / 5.197 | 0.390 / 1.628 / 3.049 |
| Outer B | 11.153 / 6.116 / 9.530 | 8.995 / 5.220 / 8.604 |

All four native crop sheets were visually inspected with photo targets and
old/new fixed-mesh markers. Candidates remain near canthal regions, but
small lower/outer shifts and finite generic eyelid detail prevent treating
them as exact anatomical truth. Some gains are comparable with the manual
reading uncertainty. No inference about identity improvement is justified.
Profile-view visibility and the consequences of refitting pose using these
candidates have not yet been established; these are the next checks.

Private `canthus-support-v2` retains per-anchor candidate IDs, visibility
counts, distances, errors and corrected-layout three-view sheets. An initial
v1 layout overlapped rows; it was not used for visual conclusions. Both
outputs remain private and the source data were not overwritten. The runner
verifies input consent and source/camera hashes. All 72 tests pass. No
upstream implementation code, external model or private service was used.
