# Experiment 0137: profile material-support camera audit

Status: `TECHNICAL_CHECK_PASSED` for the fixed-point replay; experiment-0135
camera promotion remains `REJECT`. Camera and reconstruction acceptance remain
`UNVERIFIED`.

Experiment 0135 selected a nonzero profile-camera rotation from the same traced
silhouette that it scored. This experiment asks a narrower question before any
further shape fitting: does that camera movement also help recognizable material
points which are not defined by the moving outer contour?

Keep the experiment-0132 head, intrinsics, camera centers and camera-rotation
direction fixed. Lift ten Face Landmarker locations from the front photograph
onto the unchanged head as exact barycentric surface points. On each profile,
visually retain only the near-eye and lip/subnasale points which identify actual
material features; exclude the far eye, the view-dependent nasal-tip contour and
source points hidden behind the visible profile surface. This leaves six points
on the left and seven on the right. The profile detections remain provisional:
this is a cross-view diagnostic, not accepted landmark truth.

Replay the full experiment-0135 rotation direction at 101 fixed scales from zero
through one. The previously selected silhouette scale is 0.76. On the reviewed
material points it changes mean pixel error as follows:

| Profile | Experiment 0132 camera | 0135 scale 0.76 | Change |
| --- | ---: | ---: | ---: |
| Left | 9.0087 | 9.1528 | +0.1440 |
| Right | 10.2408 | 10.8358 | +0.5950 |

The minimum summed reviewed-point mean over the complete 101-step scan is the
unchanged camera at scale 0.00. Individual points move in both directions; on
the right, one near-eye point improves by 0.18px while its partner worsens by
0.66px, and the upper-lip points worsen by roughly 2.4–2.6px while two lower
points improve. Native-resolution overlays were inspected. The selected 0135
movement is only a few pixels and does not provide a coherent material-feature
gain to accompany its same-trace silhouette gain.

All surface points remain fixed; no mesh, observation, source photograph or
default camera is changed. The local output records source hashes, per-point
surface-visibility gaps, all 101 trials and both annotated photographs. The
five authorized photographs and derived overlays remain under ignored private
storage.

This does **not** prove the experiment-0132 cameras are calibrated. Full-profile
Face Landmarker coordinates are outside the project's acceptance evidence, the
head geometry is still unaccepted, and detector/manual reading uncertainty is
larger than some measured changes. It does falsify the stronger interpretation
that experiment 0135 found a generally better profile camera: its gain does not
transfer from the fitted silhouette to this separately defined material-support
set. Preserve 0135 as `PARTIAL_SUCCESS` only for its contour diagnostic and
`REJECT` it for camera promotion.

Next keep the experiment-0132 cameras as the experimental reference and test
subject-specific central-face geometry against both contour and reviewed
material supports. Do not tune the profile pose farther on the same silhouette,
and do not use these provisional points as a camera-acceptance gate.
