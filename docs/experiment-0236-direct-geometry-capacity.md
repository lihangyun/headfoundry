# Experiment0236: directly predict geometry on a coherent known3D head

Date:2026-10-19. Pre-registered before implementation/inference. Status:`REJECT`.

0235 freezes context-assisted point-patch refinement. Do not revive it. Existing
0018 DA3-BASE inference used the subsequently identified independently generated
five AI references; its camera failure is not evidence about this coherent scan
sequence. Test a different mechanism: the already installed, separately locked
Apache-2.0 DA3-BASE directly predicts multi-view cameras/depth from images.
No new model, weights, training, Internet/API or fallback is authorized/needed.

Use exactly0230-upright's six existing clay source-scan images (front,yaw-10,
yaw+10,yaw-30,yaw+30,pitch+10), unchanged geometry, visibility and camera archive.
The model receives only RGB pixels, never known K/E/points/scan, masks or
correspondences. Area-resize720x1280 to378x672 (both multiples14, unchanged9:16
aspect); no crop, warp or padding. Preserve the existing square-photo runner's
default behavior. Pixel conversion is explicitly OpenCV array-center zero,
resize q'=(q+.5)*.525-.5, known archive centers minus.5. First reference, CPU FP32,
four threads, seed18, default pose decoder, same strict safetensors alias load.
One inference,180s process budget, at most6 views. No model-size, pose-decoder,
resolution, mask, focal, appearance, confidence or input-view search afterward.

Evaluate two distinct outputs without any camera/shape optimization:

1. Camera-only: triangulate exact known material observations from fixed front
   and yaw-10 under predicted K/E; project into the other four views. Each fixed
   population is common first-hit-visible in all three images and within the
   existing100..620 by500..820 box. Keep all samples, including behind-camera or
   invalid predictions as failures. Require>=200 points,>=50px source span,
   proper rotations, plausible focal400..3000 original pixels, all positive
   depths, all two-source and independent-view p95<=3 original pixels. The exact
   known cameras must pass the identical evaluator first. No re-alignment or
   point/error pruning. Report relative rotation and translation-direction errors
   separately, not as a proxy for reprojection acceptance.
2. Joint camera/depth: bilinearly sample predicted frontal z-depth at exact
   source observations, unproject using predicted K/E only, and project into
   each other view. Same fixed two-view visible/boxed population,>=200 points,
   positive depths, no confidence selection, p95<=3 original pixels in all5.
   Depth-convention unit checks and the exact-camera/exact-depth oracle precede
   inference. This combines geometry and pose errors; never call it camera-only.

Save source/model/runtime hashes, exact pre-registration and producer, all raw
predictions and per-point projections/errors, actual white-clay observation
overlays and relative pose diagnostics. A pass in both lanes permits one
separately frozen real-video check, not a full head or scan/likeness acceptance.
A failure stops this controlled initializer configuration without stronger-model
or conditioning rescue. Clay-to-real domain transfer remains unverified even
if it passes. Source scan renders are truth diagnostics, not reconstructed output.

Protected:original scans/videos and old failures unchanged; case002 reserved;
no training/upload; no production asset/camera/default change; no Peek/private
service reuse. Keep the full video-only editable-head, fixed scan-region,
global-alignment, bilateral profile and actual visual acceptance goal intact.

## Single frozen result

Offline inference completes once in24.39s (26.33s total);174 regression tests pass.
The exact camera evaluator and exact source-point z-depth oracle pass before ML.
Weights/source/runtime and original source files pass strict identity checks.
All predicted rotations/formats/focals pass structural checks and all evaluated
points have positive depth, but none of the independent accuracy cases passes.

| Target | Camera-only independent p95 px | Joint depth+pose p95 px |
| --- | --- | --- |
| yaw-10 | source pair, not independent | 15.464279 |
| yaw+10 | 15.500441 | 10.668195 |
| yaw-30 | 25.945627 | 23.070409 |
| yaw+30 | 93.707232 | 77.865995 |
| pitch+10 | 22.294335 | 7.101182 |

The two triangulation-source reprojection p95 values are only1.22-1.30px;
they emphatically do not predict the third-view errors. Relative rotation errors
are0.75-3.43degrees, translation-direction errors1.28-3.48degrees. Predicted focal
values are structurally plausible but not calibrated (1468-1768px versus known
1083.26px). Actual per-view source-clay overlays were inspected and retain the
large directional offsets. No precision can be inferred from positive depth or
apparently small angle errors alone.

Stop this exact direct initializer configuration. Do not rescue it by changing
decoder, model, focal conditioning, appearance, resolution or point confidence.
This is a clay-domain falsification, not proof that this model never works on
photos. No real-image transfer, shape fusion, production change or accepted
reconstructed head follows. Private records retain raw predictions, all point
arrays, immutable pre-registration, successful oracle, comparison and full logs.

The remaining evaluation infrastructure must not be bypassed: source-valid scan
regions and one declared whole-head similarity are still not frozen. Establish
exact triangle-surface distances and explicit region/transform provenance before
another video-head candidate is scored in millimeters; do not replace those
requirements with another image-only median or a nearest-vertex score.
