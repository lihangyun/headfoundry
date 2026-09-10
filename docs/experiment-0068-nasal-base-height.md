# Experiment 0068: nasal-base vertical control

Status: `REJECT` for shape promotion. Original model and cameras unchanged.

Add only the paired nasal-base down/up control to the three-control, visible
alar-observation experiment 0067. Both official graphical target files at
the existing pinned revision explicitly declare CC0; exact hashes and scope
are in `examples/makehuman-nose-base-lock.json`. Parse source deltas with the
existing independent parser and map original source IDs. No trained weights
or upstream application implementation are imported.

The source, original cameras, twelve visible alar observations, bilateral
nasal curve samples, priors and bounds remain fixed. In particular the
frontal projection prior uses the original six-target affected-vertex set;
it is not silently expanded. Four signed controls require sixteen sign
branches, all converged. Select minimum training cost (13.320010).

Best tip/depth/width/base coefficients: 0.314844, -0.031544, -0.069586,
-0.201022. Positive tip means up; negative base means down. Maximum movement
0.010357 template units, maximum frontal prior-set shift 3.861505px. No
reversed triangle normals; minimum area ratio 0.727371. This does not prove
anatomical correctness or self-intersection freedom.

| Fitting diagnostic px | Source | Candidate |
| --- | ---: | ---: |
| Front alar mean | 8.8148 | 5.6963 |
| Left30 near alar mean | 5.1659 | 5.9367 |
| Right30 near alar mean | 4.8562 | 3.8662 |
| Left nasal profile MAE | 2.8416 | 3.1264 |
| Right nasal profile MAE | 6.4675 | 6.6559 |

Actual same-camera five-view renders were inspected. The added degree of
freedom reduces frontal alar misalignment but trades against left-oblique
and both nasal profile evidence. No visible identity improvement or baseline
promotion is justified. This supports the narrower conclusion that the
base-height mode can move the frontal support in the desired direction;
it does not establish that the source must simply be lowered, because
detector/anatomical correspondence and cameras remain uncertain.

Private `authored-nose-base-v1` retains the actual OBJ, all branch costs,
complete diagnostic report, asset lock, five-view sheet and final surface
audit. The local fitter accepts `--base-height`, preserves old defaults,
verifies source/support assets and consent, and does not overwrite outputs.
All 72 tests pass. Next separate the frontal alar reading/correspondence
uncertainty from shape error before increasing the strength of this mode;
repeating a larger bilateral-regressing deformation is not a quality path.
