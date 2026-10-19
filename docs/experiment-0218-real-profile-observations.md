# Experiment0218: independent real-video profile contours

Date: 2026-10-19. Measurement execution: `TECHNICAL_CHECK_PASSED`.
Observation precision screen: `REJECT`, stopped before camera fitting.

0217 confounded fixed material points with view-dependent skin contours and
detector estimates on untextured scan geometry. Test a directly observed signal:
skin/background profile edges in the two real development frames139 and416.
The visual target is a source trace following nasal bridge/tip, lips and anterior
chin. Geometry and cameras are not fit in this observation screen.

Use the largest connected positive R-B foreground in fixed half-open image ROIs
frame139:[400,630,590,843] and frame416:[120,630,320,843]. Interpolate the R-B zero
crossing between adjacent pixel centers, preserving every row without smoothing.
Reject missing rows and search-window clipping. This explicitly relies on these
blue backgrounds; it is not a general skin/identity detector.

Primary variable: contour observation definition. Perturb the color threshold
by+/-4 units only to measure uncertainty, never to select a best-fitting trace.
Require perturbation p95 <=2px and actual source-image visual review. A failed
measurement stops this configuration without threshold/window sweeps.

These traces provide independent input-side evidence of the visible boundary,
not camera ground truth, fixed3D material correspondences or a reconstructed
head. Their image and row samples are development observations, not an independent
benchmark. The same surface row can belong to different3D points in different
views. Retain case002 for later method validation.

Budget: one measurement, at most60 seconds. Source files, consent, previous
failed experiments and production defaults remain protected. Reuse existing
NumPy/Pillow/SciPy and the established profile-envelope helper when a separately
justified camera or geometry experiment follows.

## Actual result and stop

All213 rows in each view have an unclipped crossing, but threshold perturbation
p95 is9.60px in frame139 and4.00px in frame416, exceeding2px. Maximum shifts are
24.00px and41.11px respectively. Actual source-edge review shows a generally
plausible nasal edge but unstable dark-lip/contact and lower-chin readings.
The largest connected component does not resolve neutral-colored foreground.

Reject these precise-boundary observations. Do not change thresholds, smooth
the traces, trim their worst rows or fit cameras using them. The failed source
traces and uncertainty alternatives remain in the private pilot. This outcome
does not mean the visible profile is unmeasurable; it falsifies this specific
absolute-color crossing as sufficiently precise evidence.

Two focused tests pass: exact subpixel crossings with detached color noise and
fail-closed handling of missing/clipped observations. No model, shape, default,
case002 data or external service changed.0219 tests a separate real texture-track
mechanism, rather than another boundary threshold.
