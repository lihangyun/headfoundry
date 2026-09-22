# Experiment 0146: semantic profile-region audit

Status: deterministic partition/audit `TECHNICAL_CHECK_PASSED`; observations
remain fitting evidence; geometry and camera unchanged.

This experiment changes no reconstruction variable. It partitions the existing
bilateral pure-profile observations into upper bridge, nose, mouth and
chin/jaw regions, then replays the unchanged experiment-0132 mesh and cameras.
Hair/cranium, rear neck and artificial cut boundaries are explicitly excluded.
The partition was visually inspected on the authorized photographs. It is a
manual semantic reading of existing fitting observations, not independent
ground truth.

Mean absolute errors in pixels:

| Region | left90 | right90 |
| --- | ---: | ---: |
| Upper bridge | 3.00 | 8.46 |
| Nose | 0.84 | 3.10 |
| Mouth | 3.44 | 5.76 |
| Chin/jaw | 5.12 | 4.22 |

The nose tip/base is not the dominant remaining profile error. Mouth and
chin/jaw are worse on both sides, while the right upper bridge is a separate
asymmetric issue. Maximum individual errors still reach 13.81 px left and
13.10 px right. The visual overlay confirms the reported point-to-model
directions; rings are the existing photo readings and solid points are the
fixed-model intersections.

The audit path is `TECHNICAL_CHECK_PASSED`, but no visual or geometry promotion
follows because all points were already part of the development evidence. Do
not respond by increasing global scale, fitting hair, adding another nose-only
field or weakening bilateral/front protections.

Next gate: test one structured mouth-plus-chin/jaw deformation family with the
nose region, every existing eye support, frontal/oblique outlines and mesh
safety protected. The right upper bridge must be reported separately rather
than allowed to bias the lower-face solve. Reserve samples within each lower
region for transfer reporting even though they are not independent photos.
