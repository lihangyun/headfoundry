# Experiment 0117: audit profile observations before further fitting

## Question and controlled comparison

Can correcting misplaced mouth silhouette observations recover visible lower
lip relief? Enlarged local photo overlays show original samples outside the
left outline and inside the right lower lip. Preserve those original records.
The candidate changes only 13 x readings (7 left, 6 right), retaining the same
y coordinates, sample counts and all other observations. Maximum corrections
are 24 and 12 pixels. A local RGB-gradient trace with continuity regularization
was visually inspected; it is provisional, not independent ground truth.

Keep experiment 0115's mesh, cameras, three depth controls, initial parameters,
bounds, prior and optimizer fixed. Protect retained head and stitched boundary
coordinates exactly. Predict restored lip relief in both profiles; reject the
hypothesis if the lower control stays flat or actual views show no meaningful
likeness improvement. Local artifacts are `corrected-lip-row-fit-v1`, with
before/after OBJ files, numerical report and five-view/mouth comparisons.

## Executed result

| Measurement rows | Before left/right MAE (px) | After left/right MAE (px) |
| --- | --- | --- |
| Original | 5.6565 / 6.2076 | 5.9156 / 6.1232 |
| Corrected | 4.5445 / 6.1848 | 4.6814 / 5.9367 |

The solver terminates successfully but lower-lip amplitude remains effectively
zero (-2.21e-14). Actual five-view comparisons retain generic identity and flat
lower-lip shape. Candidate promotion is `REJECT`; the saved numerical report's
initial `UNVERIFIED` state is not an acceptance result. No baseline changes.

The annotation mistake is real, but correcting it alone is insufficient.
Historical profile scores must not be treated as accurate photo-boundary
ground truth or compared to corrected-label scores as algorithmic improvements.

## Additional discriminating check

With corrected-fit parameters fixed, independently perturb only lower-lip
amplitude by -0.0001, -0.001 and -0.01. Every perturbation affects only 4 of
33 sampled silhouette rows. Maximum pixel shifts are 0.0306, 0.3061 and 3.0809.
Photo-only squared residual rises from 1483.1274 to 1483.3478, 1485.5576 and
1530.1324 respectively, without including the parameter prior.

Thus the collapse is not solely caused by the regularization term: the current
photo objective itself discourages this tested relief direction. This local
check does not distinguish wrong cameras, wrong shape basis or remaining
observation/support errors. It does rule out simply removing the prior as an
evidence-backed remedy. Do not repeat this three-control silhouette fit.
Next investigate shared camera/correspondence support and broader shape
constraints; keep held-out camera evidence separate from fitting observations.

All private photos, meshes and overlays remain local-only. Existing camera
thresholds and clean-room restrictions remain unchanged. No texture, expression
or KeenTools/MV-HRN quality claim follows from these checks.
