# 0394 continuous pipeline: curve observations

2026-10-30. Single change: represent a sliding boundary by distance to its
observed polyline, rather than assigning each sampled boundary location a fixed
material identity. Initial implementation budget30minutes using existing NumPy.
Keep stable point factors separate. No actual patient fitting in this step.

0242 measured failure of fixed frontal detector attachments.0244-0246 used
horizontal outer-profile envelopes; this component instead supports explicit
ordered 2D anatomical curves, including lips, with endpoint and segment-switch
semantics. It does not itself establish which model vertices form those curves.
0382 render-redetection did not supply an accurate physical camera; do not use
its semantic pass to certify these observations.

Implement exact point-to-polyline residual and local active-segment derivative.
Interior segment motion along its tangent must not become shape error. Beyond
an endpoint, use distance to that endpoint. Report closest segment/fraction and
ties; derivative is local and cannot be claimed smooth at segment switches.
Do not silently skip invalid/degenerate segments. Test tangential resampling,
normal displacement, endpoints, ties and numerical derivative agreement.

Real input preparation uses archived0303native XY only, with source hashes and
fixed frames240/300/630. Keep upper/lower lip curves separate so nearest-point
association cannot silently jump between them. Detection curves remainUNVERIFIED;
anatomical and visibility review is required before fitting. Original camera3px,
medical2mm and whole-head acceptance remain separate. Next integration needs
visible model curves and region-wise source review, not a new detector install.

## Implemented and exercised

`headfoundry.curve_observations.point_to_polyline` returns native residuals,
local2x2Jacobian, chosen segment/fraction and ambiguity flags. Exact endpoint
transitions and equal-distance segment ties are flagged. No global smoothness
claim. Three focused tests pass, including finite-difference derivatives away
from switches and the distinction between tangential slip and normal error.
This factor is one-directional; a future whole-curve objective must also enforce
coverage to prevent a short predicted curve explaining only part of the target.
Polyline topology/visibility and anatomical identity are not solved by distance.

`tools/prepare_lip_curves.py` ran once in1.48s using existing0303predictions;
no new neural forward or deleted integration restored. Verified frozen archive,
authorized original video and full-frame ledger hashes. Four official mouth
chains of11vertices each were checked against the installed MediaPipe graph.
Produced all four curves in native frames240/300/630, with minimum segment
lengths6.3754/3.8102/2.2872/2.2425px. No missing/zero-length segment occurred.

Local bundle `assets/private/reconstruction-observations-v1/lip-curves.npz`
and manifest retain frameRGB/source hashes, curveIDs and arrayhash. All are
UNVERIFIED pending anatomical/visibility review; no uncertainty values fabricated.
This makes actual lip observations available to the evolving pipeline, but does
not establish a better camera, head or medical result. Next work is source review
and a visible model-curve attachment that does not repeat0242's fixed frontal
point hypothesis. Keep this functioning component and data bundle while completing
that integration; no failed experiment debris was generated in this step.
