# Experiment 0088: transfer existing joint camera to excluded seam samples

Status: `UNVERIFIED`; no camera/default promotion.

Before another camera solve, evaluate experiment 0079's existing hash-pinned
actual-head joint pose on seam samples 13/14. Those two samples were excluded
from that pose objective, which used reviewed canthi, mouth corners and alar
samples. They have been used elsewhere in development; they are not pristine
acceptance data. No camera or shape is optimized in this transfer check.

Repeating experiment 0087's free-point fit with the joint cameras gives
front/left/right errors 3.9675/4.0191/0.4189 px for sample 13 and
4.2818/4.2341/0.5219 px for sample 14, versus original-camera errors
5.6948/5.1095/0.9998 and 6.0099/5.3305/1.1239. Frontal predictions from the
two obliques remain 6.2175/6.7101 px, so consistency is still insufficient.

Also evaluate the actual exported joint head with its own cameras and unchanged
barycentric seam supports. Exact face ordering matches the source. This avoids
inferring real-head improvement from unrelated free points:

| Fixed-support errors px, samples 13 / 14 | Original head/cameras | Joint head/cameras |
| --- | ---: | ---: |
| Front | 0.3748 / 1.9445 | 0.3748 / 1.9445 |
| Left oblique | 10.6504 / 14.1292 | 8.5725 / 10.0881 |
| Right oblique | 6.2781 / 10.3163 | 5.2563 / 6.4939 |

This is positive transfer to excluded seam samples, but leaves substantial
actual-head error and the prior visual limitations. Do not claim identity
improvement or camera acceptance. The joint camera still has active rotation
bounds and the original profile views remain unchanged.

Decision: use this existing coupled configuration as an explicitly unaccepted
comparison in the next mouth experiment, instead of repeatedly fitting against
only the original cameras or inventing a seam-only camera correction. Recheck
actual profile and all-view rendering for any new shape. All raw inputs and
private outputs stay local; no public production changes. Private
`seam-multiview-joint-camera-v1` records free-point and leave-one-view results.
