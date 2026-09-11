# Experiment 0077: nasal midline consistency without a mesh

Status: `UNVERIFIED` diagnostic; no camera, annotation or mesh changed.

Before treating the angular nose from 0076 as only a shape problem, remove
the mesh entirely. For detector IDs 4 and 2, fit a free 3D point to front and
both oblique observations under each existing camera set. Three pair-based
initializations converge to the same cost. Check finite solutions and positive
depth. Also fit every two-view subset and project into the excluded view.
The detector IDs are candidate shared correspondences, not verified anatomy.

| Camera | Point | Three-view fit errors front/left/right px |
| --- | --- | --- |
| Original | 4 | 10.427 / 9.246 / 1.898 |
| Original | 2 | 7.000 / 6.046 / 1.530 |
| Canthus-contour | 4 | 8.359 / 8.697 / 0.505 |
| Canthus-contour | 2 | 5.394 / 5.686 / 0.452 |

With both obliques locating the free point, original-camera frontal prediction
errors are 16.2707px (4) and 10.9251px (2). Canthus-contour gives 13.0211px
and 8.3996px. Thus greater mesh freedom cannot by itself make these particular
fixed-camera observations consistent. This is not proof of a global optimum
or a separation of camera, detector and expression errors.

## Shared vertical-bias diagnostic

Fit free 3D positions for the two midline and six alar points, retaining the
previous explicit visibility mask. Add only two shared image-y offsets, one
for each oblique view; front fixes the gauge. Offsets are limited to +/-30px.
This changes neither saved cameras nor observations. All-eight-point mean
errors drop from 4.5756 to 1.1453px with the original cameras, and from 3.8015
to 0.8465px with canthus-contour. More parameters make a lower training error
expected; that decrease alone is not evidence of calibrated cameras.

To check transfer, estimate biases using only the six alar points. Freeze
them, fit each midline 3D point using its two oblique observations, and predict
its frontal location without using that frontal observation in either solve:

| Camera | Alar-only left/right y biases px | Frontal error point 4 px | Frontal error point 2 px |
| --- | --- | ---: | ---: |
| Original | -9.1426 / -6.1967 | 8.2153 | 2.9872 |
| Canthus-contour | -8.2941 / -4.7262 | 6.1782 | 1.5997 |

These excluded observations are only withheld from this diagnostic, not from
all historical camera/source fitting. They cannot replace the frozen camera
acceptance tracks. Camera pose/crop and systematic detector localization remain
possible explanations for the common offset. Tip-specific disagreement remains
after the shared correction; do not relabel the estimated biases as camera truth.

Actual three-photo observed/projected midline overlays were inspected. Keep
midline point 4 out of hard three-view deformation targets. Next test shared
camera/observation alignment against non-nasal facial anchors and contours,
while separately reviewing tip correspondence. Merely smoothing or increasing
nasal displacement cannot resolve the fixed-camera ray inconsistency.

Private `nasal-midline-consistency-v1/v2/v3` retains each stage, with v3 the
complete audit, pinned input/camera digests, all starts, pair predictions,
visibility masks, bias estimates and actual photo overlays. No identity data
is committed. Existing production APIs/defaults and acceptance gates unchanged.
