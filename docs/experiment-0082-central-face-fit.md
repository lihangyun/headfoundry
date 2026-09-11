# Experiment 0082: central-face control fit

Status: `UNVERIFIED`. No mesh, camera or product default changed.

Fit five paired symmetric controls prepared in experiment 0081: eye spacing,
cheek volume, chin height, chin prognathism and chin width. The source is the
unchanged experiment-0040 `oblique-jaw-v3` head, and all five cameras remain
the unaccepted `template-registration-v3` registration. The experiment-0079
joint nasal candidate is not used. Shape is the only optimized variable.

The fit uses the same four frontal/oblique outlines, both complete profile
curves and reviewed non-nasal anchors used by experiment 0080. Far-side mouth
observations remain excluded where the source mesh self-occludes. Each signed
control is selected from its decrease/increase pair, requiring 32 deterministic
sign branches. Coefficients are bounded to 0..0.5 with a weak source prior.

| Diagnostic px | Original source | Central-face candidate |
| --- | ---: | ---: |
| First frontal outline MAE | 4.6891 | 4.5316 |
| Second frontal outline MAE | 7.6932 | 6.9453 |
| Left-oblique outline MAE | 3.1510 | 2.0857 |
| Right-oblique outline MAE | 2.3937 | 1.6953 |
| Non-nasal anchor mean | 5.2265 | 5.0210 |
| Left profile MAE | 3.6420 | 3.5978 |
| Right profile MAE | 8.0322 | 7.7476 |

Fitted signed coefficients are eye spacing `+0.12399`, cheek volume
`+0.26892`, chin height `+0.02211`, chin prognathism `-0.00351` and chin width
`-0.11399`. No coefficient reaches a bound. Maximum vertex displacement is
0.02544 template units. There are no reversed triangles and the minimum
triangle-area ratio is 0.92516, so this candidate avoids the mesh-quality
failure that rejected both experiment-0080 candidates.

These are fitting measurements, not independent validation. Actual five-view
photo/source/candidate renders were inspected. The cheek and chin changes are
visible but small; the side silhouettes improve only slightly, while the eyes,
nose, lips and overall head remain visibly generic. The material right-profile
error also remains. The result does not yet provide a final human-judgeable
identity reconstruction and cannot support a KeenTools-quality claim.

All target assets are CC0, pinned by revision and SHA256 in the public lock.
The private basis, identity-bearing mesh, report and five-view comparison stay
under Git-ignored `assets/private`. Input rights, asset hashes, source mesh,
cameras and photo hashes are checked before fitting; mismatch fails closed.
No paid or noncommercial model and no external private service is used.

Decision: retain this only as evidence that the narrower controls are stable
and directionally useful. Do not promote or repeatedly tune the same five
controls against the same fitting observations. The next gate is additional
commercially usable anatomical support for the high-impact nose/lip/eye-region
shape, followed by an actual enlarged five-view comparison with independent
held evidence. Camera acceptance and full visual acceptance remain unmet.

Full existing public suite: 78 tests pass.

## Follow-up: exported surface and support verification

Reconstructing the full mesh from the saved coefficients and pinned basis,
then applying the same neck cut, reproduces the exported candidate within
1e-12 template units with exactly matching faces. This confirms that the
measured coefficients and the displayed/exported geometry agree.

Exact ray lifting on the actual exported candidate confirms all sixteen
eligible canthus/mouth supports remain visible across the front and two
oblique cameras; the largest surface gap is below 9e-14 template units.
The two excluded far-mouth observations remain occluded (gaps 0.06645 and
0.05673). Their exclusions are still necessary after deformation.

Enlarged photo/source/candidate crops were rendered and inspected. Eye spacing
does not resolve the eyelid shape, nasal angularity or cheek anatomy. Visible
support is not evidence of correct anatomical correspondence, and these
training observations do not constitute held-out validation. The candidate
remains `UNVERIFIED`. Private `central-face-visibility-v1` retains the actual
comparison and per-support ray gaps without publishing personal data.
