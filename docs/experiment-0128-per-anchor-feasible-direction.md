# Experiment 0128: per-anchor feasible direction

## Question

Can the failed per-anchor candidate from experiment 0127 be reduced to a
nonzero update that improves the fitting objective without worsening any of
eight protected oblique eye errors or either corrected bilateral profile mean?

Freeze the candidate direction and scan 201 uniformly spaced scales from zero
to one. This changes one scalar only; cameras, actual surface supports, three
depth fields, topology, priors and observations remain unchanged. A scale is
feasible only when all ten protection slacks are at least -1e-9 px. Select the
feasible scale with lowest existing objective. This is a deterministic
one-dimensional rescue test, not another nine-parameter optimization.

## Result

The best feasible scale is 0.365. All ten protection slacks are positive; the
smallest is 0.000365 px at the previously regressing eye anchor. Both aggregate
eye and profile means improve:

| Diagnostic | Source left/right px | Candidate left/right px |
| --- | --- | --- |
| Four-eye mean | 5.471895 / 4.847883 | 4.959782 / 4.294678 |
| Corrected profile mean | 4.574355 / 6.176893 | 4.505224 / 6.139392 |

Every individual protected eye error also decreases. Maximum displacement is
0.002654 template units. Minimum triangle area ratio is 0.957157, with zero
relative normal-dot reversals and 14,417 unchanged outside-support vertices.
No parameter bound is active. These are fitting and source-relative safety
checks on provisional observations, not independent camera or likeness proof.

## Visual decision

Actual five-view photo/source/candidate rendering completed and was inspected.
The change is visually small: generic identity and the flat lower lip persist.
The candidate is `PARTIAL_SUCCESS` as evidence that strict per-anchor protection
admits a stable nonzero coupled update. It is `REJECT` for baseline/default
promotion because it does not establish a meaningful human-visible likeness
gain. Camera, model and acceptance defaults remain unchanged.

Private `shared-surface-per-anchor-line-v1` retains the selected OBJ, cameras,
all individual errors, constraint slacks and five-view comparison. Source mesh
SHA-256 is
`fa45a8cab8bd83bf0fffe384b947e816262338a7e971e7fa9195211606752038`.
The selected direction came from a failed solver candidate, but its scale was
independently evaluated and selected only on recomputed feasible evidence.

Next work must add a shape direction that changes missing identity structure,
especially lower-lip relief and broader proportions. Repeating smaller scales
along this same direction cannot create the absent visual effect. Preserve the
per-anchor, bilateral profile and geometry safeguards established here.
