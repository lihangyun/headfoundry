# Experiment 0053: bilateral local nose/lip profile fitting

Status: candidate `REJECT` for visual promotion. Tests and projection invariants
do not establish realistic lip geometry. No baseline/default changes.

Primary variable: local shared shape under the original frozen cameras. Use
the pre-dense neck-cut source, without generic eye additions. Fit the existing
left profile rows 644–800 and right rows 647–819 jointly, preserving original
frontal camera rays and freezing all sampled profile support outside those
ranges. This targets nose-to-lip shape without changing global camera alignment,
nose tip or chin endpoint support. Targets remain approximate prior fitting
curves, not independent evidence.

The first private trial rejected a 0.354px outside-region shift: freezing the
original silhouette edge does not stop a neighboring edge overtaking it. The
second trial explicitly adds the competing edge support to the fixed set and
resolves from the unchanged current mesh. One additional fixed vertex suffices
in the first step; later steps need no additions. The zero outside-region
regression condition is not relaxed. Both trials remain available locally.

Three bounded steps of at most 0.015 template units produce:

| Step | Left local MAE px | Right local MAE px | Outside profile shift px |
| --- | ---: | ---: | ---: |
| Source | 4.3040 | 9.4491 | 0 |
| 1 | 4.0776 | 8.4986 | 0 |
| 2 | 3.6927 | 7.8068 | 0 |
| 3 | 3.3935 | 7.1606 | 0 |

Total maximum displacement 0.032698 template units; frontal projection change
at most 3.41e-13px. Final surface compared to the original has zero reversed
face normals and minimum triangle-area ratio 0.68469. This is not a global
self-intersection or anatomical-validity proof.

Actual bilateral photo overlays and identical-shading five-view clay renders
were inspected. Despite lower curve error, the right lip contour remains
angular and the clay candidate has conspicuous lip protrusions. Therefore the
numerical reduction is not accepted as a visual improvement. Increasing the
same vertexwise updates would not address this failure and is not the next step.

Private outputs `bilateral-lip-v1` retain the rejected support-regression trial
(its exported candidate is the unchanged source); `bilateral-lip-v2` retain the
three-step actual candidate, all retry/metric records, bilateral photo overlay,
five-view clay sheet and final surface audit. Runners:
`fit_bilateral_lip_profile.py`, `render_bilateral_lip.py`. Consent and source
hash checks precede fitting; identifiable artifacts remain ignored by Git.
No public code changed; all 69 tests pass.

Next test a smooth low-dimensional local deformation or lip-surface constraint
that prevents contour-point fitting from creating lip protrusions, under the
same frozen-camera and protected-region evidence. Do not adopt this candidate
as the next seed. Camera/identity/texture/completed-product gates remain unmet.
