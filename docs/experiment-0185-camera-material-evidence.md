# Experiment 0185: available material evidence for the camera gate

Status: local image/visibility audit `TECHNICAL_CHECK_PASSED`; new
camera-acceptance tracks `UNVERIFIED`. The existing 3 px numerical check
remains `REJECT`, but is not a physical-camera validation on this image set.
No new camera score or fit was run.

Experiments 0014 and 0169 already froze and evaluated six canthus and
mouth-corner readings in front and both 30-degree views. Their declared
subjective reading radii are 4–6 px, so re-reading those same points cannot
independently establish a 3 px gate. The 11 held feature tracks in
experiments 0167–0168 are concentrated around eyes/brows, with ambiguous
high-error locations and no pure-profile or rear-head coverage. Experiment
0137's profile near-eye/lip/subnasale detector locations are provisional
material-support diagnostics, not independently verified pixel truth.

Before consulting current-camera residuals, local crops of the authorized
images were inspected for additional stable correspondences.
Subnasale is a useful qualitative region but not a reproducible <=3 px
material pixel in both profiles. Nose-tip highlights and profile apices
change with lighting/view; lip-contact edges may move or occlude; chin and
jaw extrema are view-dependent contours. Each near ear appears in one
30-degree and one 90-degree view, but not an unambiguous third view.
Consequently no new spatially distributed, three-view material track was
frozen or fitted. This is an evidence limitation, not a proof that the
current cameras are correct or incorrect.

After this audit, the user clarified that the five views were **generated or
composited independently**, not rendered from one fixed 3D scene or captured
from one real subject in a single session. This first-party provenance
statement, not missing EXIF, establishes the limitation: there need not be
one rigid head or one physically consistent camera system behind the images.
The local input manifest now describes that source. The previous 7.374 px
p95 is still the measured, failed *image-group reprojection diagnostic*, but
it cannot be attributed wholly to pose or treated as an accuracy measurement
against real camera truth. Historical reports are preserved as run records;
their physical-camera interpretation is superseded here. Do not lower the
threshold, delete difficult tracks, or tune poses to claim a passed camera.

These images remain useful as local visual targets for an experimental head,
with front and bilateral profiles compared explicitly. They cannot validate
subject identity or a physically faithful reconstruction. A physical-camera
decision needs a controlled same-subject capture (or fixed-geometry synthetic
renders with known cameras), plus independently identifiable correspondences
at suitable precision. The images, crops and linked private report remain
ignored locally and were not uploaded. Per the current user priority, the
next work is **head-mesh-only**; hair is excluded from candidate selection.
