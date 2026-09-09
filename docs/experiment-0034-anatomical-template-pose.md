# Experiment 0034: anatomical template registration

Status: `UNVERIFIED`; no head likeness or camera acceptance. Previous frozen
camera failures remain unchanged. This supplies a photo-aligned anatomical
starting point, not a reconstruction of the subject's shape.

## Experiment

Primary variable: rigid per-view pose of the unchanged CC0 template from 0033.
The prior is fixed, with no texture and no learned depth deformation. Hypothesis:
explicit anatomical correspondences can place a coherent mesh in each photo
well enough to expose its remaining shape mismatch. Counter-evidence: fixed
generic anatomy and assumed focal length can bias recovered poses.

Eight approximate template vertices were selected from a frontal raster:
four canthi, two mouth corners, nose tip and chin. Original manual observations
from 0014 supply six anchors in front/oblique views; MediaPipe supplies nose/chin
and visible profile anchors. Far-side profile anchors are excluded explicitly.
Detector outputs, especially profile points, are not ground truth. The manual
anchors are now training inputs for this new experiment, not its held-out test;
historical camera audits and their observations remain untouched.

All intrinsics are explicitly assumed: focal 1800 pixels, principal point
(627,627), square 1254-pixel photos. Six pose parameters are bounded around
view-label initialization, optimized with a robust loss. Full-mesh positive
depth is checked; vertices and topology are unchanged. No bound is active.
Per-view maximum training errors are approximately 11.15, 20.75, 10.75, 13.41,
22.08 pixels in front/left30/left90/right30/right90 order. These are not
comparable to historical held-out p95 values and do not unlock any gate.

## Actual inspected result

The five-view sheet contains original photos, clay template renders and
50-percent overlays under identical cameras. Face placement is coherent enough
to inspect nose, lips and chin. Generic cheek/jaw shape, ear placement, missing
eyeballs and the irregular shoulder/neck crop remain visibly unsuitable for a
finished likeness. Hair-covered scalp has no observed shape truth.

Private output: `assets/private/subject-001/template-registration-v3/`:
`registered.npz`, `report.json`, `comparison.png`. v1 was the inline prototype;
v2 uses the tested shared solver; v3 also revalidates every locked CC0 asset and
the exact annotation mesh against a fresh extraction. Source-image hashes and
local-only consent are validated before use. No source photos or derived
biometric outputs enter Git or an external service.

The private `register_template.py` records the approximate anatomical selection
and deterministic run; preserve existing output directories when reproducing.
Shared implementation: `headfoundry.template_pose.fit_template_pose`. A known
perspective-pose test recovers the source matrix while preserving vertices and
rejecting nonfinite, degenerate and invalid-intrinsic inputs. All 56 tests pass.

## Next gate

Keep these poses as an explicitly uncertain experimental baseline. Before
identity deformation, inspect independent profile contours and anatomical
correspondences for systematic pose errors. Then fit bounded shared geometry
with frontal protection and fixed-camera before/after evidence. Neither training
residual reduction nor a coherent generic head is sufficient for visual parity.
