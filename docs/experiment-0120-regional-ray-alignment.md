# Experiment 0120: regional alignment on the frozen current cameras

The previous cross-view lip test exposed a mainly vertical residual. Check
whether that is a common image translation before changing cameras or geometry.
Use the current joint-nasal-pose camera file, not the earlier registration
cameras from experiments 0077-0078. Keep all data and matrices unchanged.

For each detector ID, hold its frontal image ray and fit a positive depth to
both obliques. IDs: eyes 33/133/362/263, nose 4/2, mouth 0/13/14/17, chin 152.
These are candidate detector correspondences, not anatomically certified
observations; far-eye and apparent-contour semantics remain limitations.
All eleven fits converge and have positive depth in all three cameras.

| Region | Median signed vertical residual left/right (px) | Mean point error left/right (px) |
| --- | --- | --- |
| Eyes | 0.8346 / -0.1241 | 3.5987 / 3.0077 |
| Nose | 12.7736 / 7.2174 | 12.7836 / 7.4466 |
| Mouth | 7.9788 / 4.1154 | 7.8236 / 4.7786 |
| Chin | -3.2664 / -2.4070 | 3.3359 / 2.4391 |

Positive means projected points below the detector target. The signs and
magnitudes differ by region. A uniform vertical offset cannot make all these
fixed-ray residuals zero; do not apply the mouth offset to the whole image.
This does not rule out a physical pose correction, nonrigidity, or systematic
detector error, and does not establish a unique cause. No camera or shape
candidate was produced or promoted by this diagnosis.

Local `fullface-ray-alignment-v1` includes all targets, predictions and residuals,
plus an inspected three-photo overlay: green detector points, orange projected
free-ray points. The central-face vertical disagreement is visible while eye
agreement is substantially closer. The overlay is private and is not a
reconstruction improvement image. Data used in camera development is not an
independent validation set; the original held-out camera gate stays failed.

Next distinguish a physical relative-pose correction from landmark-specific
bias using broader facial correspondences and excluded-region transfer, then
test its effect on the actual shared head before any camera promotion. Avoid
uniform image shifts and further fixed-ray lip-only depth sweeps.
