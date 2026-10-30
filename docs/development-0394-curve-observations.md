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

## Source review and integration decision

`tools/review_lip_curves.py` sequentially decoded to630 and verified each required
full RGB frame against the frozen bundle. One private comparison sheet uses a
fixed[180,620,520,860]crop,2xnearest zoom, original beside overlays for all3frames.
Executed in1.54s; all three panels visually reviewed. Outer upper/lower predictions
approximately follow vermilion borders; fine localization and corner uncertainty
are not quantitatively established. Mouth appears closed in these panels: inner
upper/lower predictions overlap at a contact seam, not two separately observable
cavity rims. Retain raw curves, but prohibit treating them as independent cavity
boundary constraints. No numerical score-based point deletion was performed.
Private anatomical-review.json records this classification and pending accuracy.

Code inspection of prepare_flame_open.py and headfoundry.flame confirms the
current safe asset retains only300identity directions from400source directions;
the current adapter has no expression or jaw articulation. This creates a risk
of absorbing per-frame mouth configuration into identity. It is not a measured
causal attribution of0241errors, and adding expression alone would not fix camera
ambiguity. Before changing asset representation, review original model semantics
and existing mouth experiments; preserve the current locked identity asset.

Keep outer lip curves as reviewable observation candidates. Implement a separate
visibility-aware model-curve attachment and separate per-view articulation from
shared identity when supported. Do not force all four observed chains onto a
neutral fixed material template simply because the distance factor is available.
This is a concrete integration correction within0394, not rejection of the curve
method. No new head or millimeter improvement yet.176tests passed in9.470s at
the preceding factor implementation; this review-only addition did not rerun them.

## Native expression component retained and connected

Source inspection found original metadata `expr_source=SUPR_head`,
`expr_components=last_100`, `n_expr=100`, within the already validated official
FLAME Open pickle. The source also contains5joint LBSweights and36pose corrective
directions; their existence does not mean articulation is implemented here.
Older0149used custom nuisance modes on a different head; its failures do not
evaluate this native basis. Existing expression_contact implements paired3D
closure, not image expression recovery, and is not silently used to close lips.

Added `headfoundry.flame_expression` and `tools/prepare_flame_expression.py`.
The latter checks the existing full rights/source hash chain, uses the existing
restricted unpickler, verifies all300identity directions exactly, extracts only
the explicitly named100expression directions, and makes a separate locked NPY.
No duplicate whole model, new dependency, download or patient input is involved.
The original identity asset remains unchanged. Conversion output is private at
`assets/private/FLAME-2023-Open/expression-v1/expression-lock.json`.

Actual conversion/load completed2.13s:5023vertices,100expression components,
exact expression-basis equality and zero-expression identity replay error0.
Two focused tests pass for identity/expression separation, nonmutation and
invalid coefficients. Neutral-pose additive expressions only: no jaw/neck pose
correctives, automatic safe coefficient range, collision guarantee or anatomical
accuracy claim. The chosen coefficient bound is an engineering input limit.
No patient expression coefficients fitted and no new head-quality claim.

Next pipeline integration: determine reviewable model lip curves and visibility,
then evaluate shared identity with per-view native expression using source-only
observations. Preserve neutral export separately. Strong ambiguity/unsafe geometry
must be reported; expression freedom cannot conceal failed camera/medical gates.
