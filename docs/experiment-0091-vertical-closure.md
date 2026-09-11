# Experiment 0091: actual lip section and vertical-only closure

Status: `REJECT` for promotion; no accepted mouth configuration.

Extract 61 triangle-intersection segments at x=0.00001 through the actual
coupled head, with explicit y/depth bounds around the mouth. Inspect the
numbered section: exterior lips turn into inner-mouth surfaces, with a gap
and substantial depth offset between the old sample projections. This does
not supply full upper/lower rim correspondence across the mouth. The pinned
base OBJ has a joint-mouth helper group, not a dedicated lip-rim body group.

Single ablation versus 0090: keep the same compact field and fractions, but
remove lateral and depth displacement, retaining only vertical attraction.
The barycentric displacement assertion is checked, and 4233 exterior-support
vertices remain unchanged. Original source and cameras are hash-verified.

Quarter/half closure has maximum movement 0.002444/0.004888 template units,
zero reversed triangles and minimum area ratios 0.960149/0.921321. Left
profile MAE changes from 3.589129 to 3.586720/3.584437 px, while right worsens
from 7.249347 to 7.285239/7.318458 px. At quarter closure the lower sample is
already occluded in both obliques; at half closure it is occluded in all three
front/oblique views. Ray gaps reach approximately 0.024 template units.

Inspected actual enlarged frontal/bilateral clay renders retain the angular
lip form and do not provide convincing natural closure. Removing depth motion
does not cure the support problem. Do not repeat two-point compact attraction:
the next implementation must model the lip rim as a surface curve and allow
visibility to change consistently with contact, rather than use old interior
samples as immutable seam observations. Occlusion alone is not proof of
collision or invalid closure, but invalidates those samples as visible fitting
constraints. No visual improvement or collision freedom is claimed.

Private `lip-section-v1` retains actual intersection coordinates and diagram;
`seam-vertical-closure-v1` retains meshes, report and inspected comparison.
Public production code remains unchanged. Validation: actual section, field
assertions, triangle checks, ray visibility and rendered comparison.
