# Experiment 0147: structured lower-face depth spline

Status: solver replay `TECHNICAL_CHECK_PASSED`; every nonzero candidate and
geometry promotion `REJECT`.

This experiment changes one shape family with every experiment-0132 camera
fixed: four smooth bilateral z-axis modes centered on mouth, chin, lateral jaw
and the lower-face transition. Unlike the exhausted independent camera-ray
fields, these modes are defined in frontal anatomical image space, share one
left/right geometry update and can alter frontal projection. Nose observations,
four eye supports in three views, all existing frontal/oblique outlines and
triangle orientation/area are protected.

Existing mouth/chin profile samples are interleaved into fitting and transfer
subsets within each side. These subsets come from the same photographs and are
not independent acceptance evidence. The fitted four coefficients are scanned
over twenty nonzero scales; real silhouette associations are recomputed for
every scale rather than trusting the optimizer's local support.

At the smallest 0.05 scale, training means improve bilaterally from
3.113/4.934 px to 3.082/4.876 px. The left transfer mean improves from 5.849 to
5.775 px, but the right transfer mean worsens immediately from 4.594 to 4.607
px and continues worsening as scale increases. Nose means stay essentially
unchanged, every outline mean improves, minimum triangle-area ratio is 0.991
and no tested normal reversals occur. Thus the first failure is the bilateral
transfer conflict, not mesh safety or the protected upper face.

Zero is the only admissible selection. The numerical runner is
`TECHNICAL_CHECK_PASSED`; all nonzero geometry is `REJECT`. Do not accept a
same-photo training gain by weakening the right-side transfer guard or by
making the symmetric family asymmetric without new evidence.

Next gate: re-audit the conflicting right-profile lower-face observations and
their camera/correspondence uncertainty against the locked Blender overlay.
The discriminating question is whether the conflict comes from semantic point
placement, expression/pose difference, camera error or true asymmetry. Do not
run another lower-face geometry family until that evidence is separated.
