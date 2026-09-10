# Experiment 0059: bounded whole-head shape fitting

Status: `UNVERIFIED`. No source promotion and no claim of visible identity
improvement. Camera and complete reconstruction gates remain unmet.

Use the four authored CC0 targets prepared in 0058 on the original 4459-vertex
oblique-jaw-v3 topology. Verify base/target hashes, licenses, revision, source
mesh and camera hashes, input consent, and oblique observation photo hashes.
Keep cameras fixed. Fit four nonnegative coefficients bounded at 0.5 using
robust least squares (soft-L1), 5px observation scaling and coefficient prior.
Run two initializations (all 0.01 and all 0.25); both converge, with costs
24.373677 and 24.379165. Choose the lower training cost, not a profile score.

Training observations are the existing 12 frontal lower-oval detector points,
10 inspected oblique photo-boundary points and masked eight template anchors
in front/left30/right30. The two profile curves are excluded from this solve
but were used in source construction; they are regression checks, not new
held-out truth. The source-defined front-half triangle ROI for the fitting
outlines stays fixed. Full-source edge envelopes are used for profile checks.

Coefficients (diamond, oval, rectangular, round): 0.155432, 0.190055,
0.078173, 0.217566. None reaches a bound. Maximum displacement is 0.049483
template units, no reversed triangle normals, minimum area ratio 0.483900.
These checks do not prove absence of self-intersections. Neck clipping occurs
after deformation, not by inventing correspondence for new cut vertices.

| Diagnostic, pixels | Source | Candidate |
| --- | ---: | ---: |
| Frontal first outline MAE | 4.6891 | 3.6761 |
| Frontal second outline MAE | 7.6932 | 4.1162 |
| Left30 outline MAE | 3.1510 | 2.7033 |
| Right30 outline MAE | 2.3937 | 1.9046 |
| Anchor mean distance | 6.8586 | 6.9436 |
| Left profile MAE | 3.6420 | 3.6445 |
| Right profile MAE | 8.0322 | 8.0312 |

The actual five-view photo/source/candidate comparison was inspected. Face
width and upper head change, but the generic eyes, nose and lips still lack
subject likeness. Outline training gains do not establish visual improvement;
anchor alignment slightly worsens and central side-profile defects remain.
The cranial changes are not directly constrained by these lower-face inputs,
and photos include hair rather than observed bare scalp. Do not interpret
the fitted cranial proportions as measured subject geometry.

Private `authored-head-shape-v1` retains actual candidate OBJ, report and
five-view comparison; `fit_head_shapes.py` retains the reproducible local
experiment. No identifiable data is committed. All 72 existing tests pass.
The result supports using bounded authored controls as a low-dimensional
fitting mechanism, not selecting this candidate as a production baseline.
Next resolve central facial anatomy and camera/correspondence ambiguity;
simply adding more skull presets is not supported by the visual evidence.
