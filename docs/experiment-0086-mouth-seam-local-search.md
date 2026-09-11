# Experiment 0086: local seam correspondence search

Status: `UNVERIFIED` diagnosis; no correspondence, geometry or camera promotion.

Inspect the actual source triangles for seam samples 13 and 14 before attempting
closure. Their separation is (0.00253, 0.00995, 0.02237) template units: depth
offset exceeds vertical offset. No open boundary edge lies within 0.15 template
units of their midpoint. Thus experiment 0085's apparent mouth opening is not
established as a missing-face hole, and the measured projected sample separation
must not be treated as a pure vertical lip gap. A connected inner-mouth surface
can still represent an open mouth. These checks do not settle configuration.

Search vertices within two topology rings of each original support triangle,
keeping the original barycentric sample as a candidate. Score only candidates
visible in all three front/oblique cameras by summed squared projection error.
All observations are selection data; no geometric deformation occurs.

For sample 13, the best candidate is vertex 468: front/left/right errors change
from 0.375/10.650/6.278 px to 5.130/6.478/3.614 px. The oblique improvements
come with a material frontal regression, so it is not promoted as a corrected
anatomical match. Sixteen of 22 candidates are visible in all three views.
For sample 14, the original sample remains best among 14 visible candidates
out of 30, with errors 1.944/14.129/10.316 px. This local vertex-only search is
not an exhaustive continuous surface or camera fit.

Decision: a nearby support swap alone is not supported as the remedy. Before
deforming lips, distinguish configuration and camera inconsistency using the
two seam samples jointly, with frontal and bilateral profile protection. Do
not collapse arbitrary sampled surface points together or weld topology on the
basis of detector labels. Existing source geometry and observations stay intact.
The private `mouth-seam-candidates-v1` report preserves positions and scores.
Checks used the hash-pinned mesh/cameras/support, consent validation, actual
triangle connectivity and ray visibility; no public production code changed.
