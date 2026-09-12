# Experiment 0102: dynamic photo-seam fitting

Status: `REJECT` for geometry promotion. Fixed-support error improves, but the
actual mouth remains angular and some originally visible supports are lost.

## Visual target and one variable

Make the closed mouth look closer to the three source photographs without
changing the existing head, cameras, profile observations, relative lip pairs,
regularization or deformation guards. The only change from experiment 0101 is
to recompute visibility and each visible rim sample's nearest point on the
photo seam after every retained fitting step.

Prediction: the frontal gap should close without introducing a pointed or open
profile, losing original visible support, worsening either whole profile, moving
more than 0.03 template units, reversing triangles or reducing any triangle
below half its source area. Failure of any visual or protected check rejects the
candidate even if nearest-curve residuals decrease.

## Result

Three bounded steps are retained with fractions 0.25, 0.5 and 0.5. A fourth
step is rejected at the smallest tested fraction because its minimum area ratio
would be 0.498556. Active seam-observation counts change 51 -> 49 -> 52 -> 53.

| Check | Source | Candidate |
| --- | ---: | ---: |
| Same 51 initial seam targets, mean px | 5.503459 | 1.967246 |
| Left whole-profile MAE, px | 3.589129 | 3.567019 |
| Right whole-profile MAE, px | 7.249347 | 6.515613 |
| Maximum movement, template units | 0 | 0.025795 |
| Minimum triangle-area ratio | 1 | 0.501975 |
| Reversed triangles | 0 | 0 |

An independent exported-mesh ray audit uses the same 26 source-defined central
rim samples. Front visibility changes 20 to 23 with no source-visible losses;
left-oblique remains 16 but loses two source-visible samples and gains two
others; right-oblique changes 15 to 14 and loses one source-visible sample.
Dynamic rematching therefore avoids the symmetric six-point loss in 0101, but
does not preserve the fixed evidence set.

The real input/source/candidate five-view sheet and enlarged frontal/bilateral
mouth crops were rendered and inspected. The candidate remains visibly generic.
The frontal seam is still a straight artificial slit; both profiles retain an
angular open shelf, and the right profile does not resemble the photographed
lip contour. The numeric reduction is real on its defined targets, but it is not
a convincing visual or anatomical improvement.

Decision: reject this candidate and stop nearest-photo-seam fitting on the
provisional central rim samples. Do not lower the area guard or reinterpret
newly visible samples as validation. Before another lip deformation, establish
a more expressive anatomical lip surface/boundary representation; otherwise
prioritize broader high-impact identity shape where the current head is still
visibly generic.

Private `photo-seam-dynamic-v1` retains the mesh, cameras, reports and inspected
images. No photograph, biometric coordinate, identity mesh or private script is
committed. Public production code is unchanged.

