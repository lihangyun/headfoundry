# Experiment 0158: fixed-camera classical stereo feasibility

Status: rectification and correspondence diagnostic `TECHNICAL_CHECK_PASSED`;
depth and geometry `UNVERIFIED`.

This experiment introduces no learned model. OpenCV 5.0 rectifies the fixed
experiment-0132 front/left-30 and front/right-30 camera pairs, applies local
contrast normalization and runs semi-global block matching inside the existing
local face masks. All photographs remain local.

The first rectification used `alpha=0`; the approximately 30-degree convergent
cameras forced an extreme crop focal length and produced roughly 17,000-pixel
spurious disparities. That invalid run is preserved and excluded. Keeping the
full rectified field with `alpha=1` produces finite 500-pixel-scale disparities.
A 5-pixel matcher window yields 4.06/5.80 px median disparity error on eleven
reviewed central Face Landmarker correspondences. Increasing only the window
to 11 pixels, to tolerate the measured 3--6 px residual vertical mismatch,
reduces the pair medians to 4.06/4.64 px. Valid masked-face coverage rises to
50.2% and 51.7%; p95 correspondence errors remain 13.7/13.0 px.

The deterministic fixed-camera rectification and dense correspondence check is
`TECHNICAL_CHECK_PASSED`. Face Landmarker disparities configure and audit the
matcher, so they are not independent metric depth truth. No disparity has yet
been promoted to a surface, camera or identity result; geometry remains
`UNVERIFIED`.

Next gate: triangulate only left/right-consistent, masked disparities from each
pair, fuse them in the fixed world frame, and evaluate the resulting front-face
surface in the unused pure-profile views. Reject depth where the two pair
estimates disagree or where profile/cheirality/mesh gates fail. A successful
technical surface still requires exact Blender visual comparison.

Follow-up: [experiment 0159](experiment-0159-classical-stereo-triangulation.md)
rejects the triangulated geometry on cross-pair agreement and unused-profile
coverage. The correspondence diagnostic above remains valid only for its
limited central-photo question.
