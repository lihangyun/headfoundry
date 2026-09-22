# Experiment 0152: side-separated lower-face shape

Status: solver `TECHNICAL_CHECK_PASSED`; geometry and visual promotion
`REJECT`.

This experiment keeps all cameras fixed and multiplies the four experiment-0147
lower-face depth modes by two soft frontal-image hemispheres. It therefore
allows the visible left and right facial surfaces to move differently without
a hard seam. Pure-profile rows drive the fit; the corresponding 35-degree
outlines, untouched profile rows, nose, frontal outline, individual eyes and
mesh safety are acceptance constraints.

The bounded eight-parameter solve converges. At the smallest 0.05 scale, both
fitted profile subsets improve, the left transfer mean improves from 5.849 to
5.801 px and both oblique outlines improve. The right transfer mean immediately
worsens from 4.594 to 4.608 px and continues to worsen as the scale grows. No
nonzero trial passes the bilateral transfer gate, so zero remains selected and
the comparison render is unchanged.

The solver and protected evaluation are `TECHNICAL_CHECK_PASSED`; every
nonzero geometry and visual promotion is `REJECT`. Softly separating the two
visible hemispheres does not resolve the conflict. This rules out a shared-side
coupling explanation for the tested four broad modes, but does not prove the
observations or current generic anatomy are correct.

Next gate: replace the single broad mouth field with an anatomically layered,
low-dimensional family for upper-lip projection, lip seam, lower lip,
labiomental groove and chin. Cameras remain fixed. The new family must improve
interleaved bilateral profile rows and same-side oblique outlines while
preserving eyes, nose, frontal outline and mesh safety. Do not add arbitrary
per-vertex freedom or reuse the rejected side split alone.
