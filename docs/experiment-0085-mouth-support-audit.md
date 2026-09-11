# Experiment 0085: inspect mouth support before further fitting

Status: `UNVERIFIED` anatomical correspondence; diagnostic only, no deformation.

Inspect detector-derived IDs 0,17,61,291,13,14 on the actual photo and the
unchanged neck-cut source under its fixed cameras. Source, camera, support
hashes and local input consent are verified first. Render enlarged paired
photo/clay crops with numbered projections and ray-visibility colors.

The photos show a closed lip seam; the clay has a visible opening and strongly
angular lower lip. The projected source samples 13 and 14 do not describe the
same closed-mouth configuration as the photo detector samples:

| View | Photo detector 13-to-14 distance, px | Source projection distance, px |
| --- | ---: | ---: |
| Front | 0.7181 | 2.6545 |
| Left oblique | 0.4436 | 4.7642 |
| Right oblique | 0.2152 | 5.8344 |

These distances are detector/projection measurements, not physical lip gap
measurements. Enlargement supports a configuration mismatch but does not
establish whether the correct remedy is support remapping, mouth closure,
local geometry or camera correction. Moving the upper/lower volume controls
cannot be assumed to correct an opening or a misplaced seam sample.

The left-oblique far corner 291 is ray-occluded and remains excluded in the
joint fit. The other samples are ray-visible, including right-oblique 61;
this is not proof of exact anatomical correspondence. Do not transfer exclusions
from different vertex supports solely because their semantic names coincide.

Next isolate the mouth opening/configuration from lip volume: inspect actual
seam topology and the source positions of both samples before selecting a
closure control or changing correspondence. Preserve bilateral nose/lip profile
checks and do not force uncertain samples into shared exact geometry targets.
No model/camera change or visual improvement is claimed. Private
`mouth-support-audit-v1` retains full-size crops and per-point targets,
projections, residuals and ray gaps. No identity-bearing data is committed.
