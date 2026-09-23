# Experiment 0175: source-visible color on one continuous mesh

Status: vertex-color projection/rendering `TECHNICAL_CHECK_PASSED`; visible
facial appearance `PARTIAL_SUCCESS`; whole-head, hair and independent
cross-view reconstruction `REJECT`/`UNVERIFIED` as specified below.

The unchanged experiment-0132 head and cameras were used for a local-only
appearance test. Skin RGB was sampled at z-buffer-visible head vertices from
front, left30, left90 and right30, excluding a dilated dark-hair mask. Missing
vertex colors were filled from the nearest same/mirrored head surface. The
right90 photo was not accessed until evaluation/render comparison. This is
**only a color holdout**: the head geometry and cameras were previously fitted
using all five photos. The private photos, colors, images and reports remain
ignored and were not uploaded or committed.

29,383/34,753 vertices received source-visible color; 5,370 were filled.
The continuous mesh removes the prominent skin speckles of the previous
20,000-point Gaussian diagnostic. Actual 512 px renders show recognizable
front, oblique and pure-profile facial appearance, including on right90.
Right90 non-hair rendered-pixel RGB L1 is 0.096, versus 0.045 on fitted
left90; these are descriptive within this test, not comparable to experiment
0174's different image/mask metric. The eye detail, facial identity and
camera alignment are not independently validated. Exposed scalp, ear/back
transitions and neck colors remain plainly wrong.

To check whether the visible face improvement hid a whole-head failure, the
colors were rendered with the already rejected gathered-hair-v2 geometry and
flat dark hair. Actual renders retain a hard hairline, exposed scalp patches,
disconnected-looking bun and simplified rear profile. Five-view hair-mask
IoU is 0.485/0.342/0.370/0.418/0.422 (front, left30, left90, right30,
right90); the rendered hair area is smaller than the observed hair in every
view. This is not a new accepted hair candidate; it confirms that plausible
facial color does not repair the rejected hair geometry.

The next gate is an explicit continuous scalp-to-bun surface constrained by
view-specific occluding contours, with both side-profile hairline and bun
silhouettes checked against the photos. Do not promote this appearance to a
formal texture or claim independent right-profile generalization while the
camera and geometry gates remain open.
