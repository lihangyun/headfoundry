# Experiment 0066: authored nasal controls

Status: `REJECT` for shape promotion. No source mesh/camera replacement.

Six graphical nose targets were inspected in the [official pinned nose
directory](https://github.com/makehumancommunity/makehuman/tree/a8bc2d54ff0ac92e78ff71431b1023eda42bf482/makehuman/data/targets/nose).
Every downloaded file explicitly declares CC0 in its header. Revision,
source paths, hashes and base license relationship are locked separately in
`examples/makehuman-nose-target-lock.json`. No application implementation or
trained model is imported. Reuse the existing independent target preparer:

```text
python -m tools.prepare_makehuman_targets assets/private/makehuman-base-v1 assets/private/makehuman-nose-targets-v1 assets/private/makehuman-nose-basis-v1 --lock examples/makehuman-nose-target-lock.json
```

Three signed paired controls are nose tip down/up, depth decrease/increase
and horizontal decrease/increase. The six targets affect 100, 77, 342, 366,
312 and 448 original head vertices respectively. The local fitter checks
base/target license, revision and hashes, prepared basis digest, source mesh,
original camera digest and photo consent. Deform the original preclip topology
then clip the neck, rather than guessing new clip-vertex correspondences.

Fixed source: oblique-jaw-v3. Fixed cameras: original template-registration-v3,
not any of the recent unaccepted pose trials. Fit bilateral curve samples
with y in 490..687px, using three coefficients bounded to +/-0.5, 5px-scaled
horizontal-envelope residuals, soft-L1 loss, coefficient regularization and
a soft prior on affected vertices' original frontal projection. That prior
is not a frontal photo measurement. Evaluate all eight sign branches from
0.1 magnitudes; all converge, and choose lowest training cost (6.376544).

Best tip/depth/width coefficients: 0.024095, -0.015249, 0.055404. Maximum
displacement 0.002108 template units, maximum affected frontal projection
shift 0.699451px, zero reversed triangle normals, minimum area ratio 0.968589.
This does not prove anatomical correctness or absence of self-intersections.

| Diagnostic px MAE | Source | Candidate |
| --- | ---: | ---: |
| Left nasal fitting segment | 2.8416 | 3.0757 |
| Right nasal fitting segment | 6.4675 | 6.3022 |
| Left remaining profile samples | 4.2022 | 4.2014 |
| Right remaining profile samples | 9.2492 | 9.2492 |

Non-nasal samples are excluded from this solve but participated in earlier
source construction, so they are regression checks, not new validation.
The actual same-camera five-view source/candidate clay sheet was inspected.
Changes are visually tiny, generic nasal/labial defects remain, and the left
nasal fit worsens. Reject promotion; adding licensed controls is not itself
evidence of improved reconstruction.

Private `authored-nose-v1` retains actual OBJ, full fitting/asset report,
five-view renders and final surface audit. All 72 tests pass. The next step
must improve the nasal observation/model support rather than amplify this
rejected three-control update. In particular, side-envelope fitting alone
does not measure nasal width or alar anatomy from the frontal/oblique photos.
