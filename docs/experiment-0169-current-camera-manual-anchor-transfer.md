# Experiment 0169: frozen manual anchors on current cameras

Status: cross-view audit `TECHNICAL_CHECK_PASSED`; camera acceptance
`UNVERIFIED`, existing 3 px gate still failed.

Experiment 0014 saved six AI-assisted original-photo pixel readings before
predicting with the then-current cameras: four eye canthi and two mouth
corners in front/left30/right30. The reading radii were declared as 4–6 px;
the coordinates were not human-verified scan truth. This experiment reuses
those exact saved coordinates, without retouching them, to check the newer
experiment-0132 camera archive. Each point is triangulated from two observed
views and predicted in the third, cycling all three targets. No camera or
head shape is fit.

Across 18 correlated predictions, the median residual is **4.559 px** and
p95 is **7.218 px**; all triangulated points have positive depth in all three
views. The largest two residuals, 7.81 and 7.11 px, concern the same less
stable far outer canthus in right30/left30. For context, experiment 0014's
different old camera candidate scored 3.049 px median and 8.226 px p95 on
the same readings. The mixed median/p95 change is not a quality win, and the
newer camera development may have used related detector landmarks from the
same photos. Do not treat these readings as a new fully independent validation
population or tune against them after inspection.

Together with experiment 0168, this confirms that the current calibration
is not established by either feature tracks or visual landmark readings.
It does not isolate pose, focal length, reading uncertainty, expression or
geometry as the cause. Six eye/mouth points cannot validate nose, chin,
pure profiles, rear head or whole-person likeness. The frozen source JSON,
current camera archive and local report are hash-linked; all photos and
identity-specific results remain ignored under `assets/private/subject-001`.
The next route must obtain spatially distributed, physically identifiable
cross-view evidence before relaxing the camera gate or promoting geometry.
