# Experiment 0083: joint nasal and lip graphical controls

Status: `REJECT` for promotion because both profile errors increase. No default
or camera changes. The technical fit and visibility checks alone are insufficient.

Primary variable: jointly optimize ten signed CC0 controls covering nasal tip,
depth, width and base height, plus lower/upper lip volume and height, philtrum
volume and vertical mouth position. This tests whether previous separate-region
fits were limited by their inability to coordinate overlapping displacements.
Reuse four existing revision/hash-locked graphical asset sets; no new model,
training data or remote service. The unchanged neck-cut source and original
unaccepted registration remain fixed. Do not combine earlier rejected meshes.

Fit both profile segments at original annotation rows y=490..819 and visible
detector-derived nasal/lip samples. Screen source ray visibility before fitting;
retain reviewed nasal side exclusions. Lip ray visibility is only an occlusion
screen, not a reviewed anatomical match. Three signed starts (zero, +0.1, -0.1)
converge in 31/45/32 evaluations with costs 40.0581/39.9827/39.9802. This bounded
multi-start test does not exhaust all 1024 sign branches. Select the lowest
training cost with weights bounded +/-0.5 and a coefficient prior.

| Fitting measurement, px | Source | Candidate |
| --- | ---: | ---: |
| Left local profile MAE | 3.7167 | 3.9786 |
| Right local profile MAE | 8.0332 | 8.2567 |
| Left whole profile MAE | 3.6420 | 3.8498 |
| Right whole profile MAE | 8.0322 | 8.2076 |
| Front point mean | 6.8406 | 5.1000 |
| Left-oblique point mean | 9.7510 | 8.7923 |
| Right-oblique point mean | 7.4747 | 6.2447 |

There are no reversed triangles or lost eligible ray-visible samples. Minimum
area ratio is 0.64745 and maximum displacement 0.01113 template units. Exported
mesh rerendering independently reproduces the triangle checks (minor decimal
rounding from OBJ serialization). These measurements are not collision checks.

Actual five-view photo/source/candidate clay renders were inspected. Changes
remain small; the generic nasal/lip shape remains visibly unresolved. Both
profile regressions contradict the intended side-reconstruction improvement,
despite the lower frontal/oblique point errors. The private numerical report
labels the output UNVERIFIED on technical checks; this documented promotion
decision is REJECT after inspecting all-view evidence.

This rules out treating a joint ten-control fit as sufficient under the current
observations and objective. It does not prove the basis cannot represent the
subject. The next discriminating step is to audit mouth correspondence semantics
and use explicit side-profile protection when combining point and contour fits;
simply adding more controls or repeating starts has no supporting evidence.
All observations here are fitting data or previously used diagnostics, not
independent held-out truth. Camera and likeness acceptance remain incomplete.

Private runner `fit_nasolabial.py` retains input consent and pinned asset checks;
`joint-nasolabial-v1` retains the exported mesh, fit report, independent exported
mesh checks and actual photo comparison. No personal data enters Git. Public
production code was unchanged; verification consisted of the real three-start
solve, candidate support checks and exported five-view rendering.
