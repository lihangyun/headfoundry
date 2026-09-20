# Experiment 0134: MediaPipe relative-depth prior

## Question

Does the already-local, Apache-2.0 MediaPipe Face Landmarker contain a stable
subject-specific depth signal that can replace further generic nose/lip target
tuning? Keep the 0132 head and cameras fixed. First align learned relative depth
to current camera depth outside a central ellipse; then test one fixed six-point
nose/lip direction under the existing bilateral profile, eye and mesh guards.

The single-front audit explains 88.8% of retained exterior depth variance. A
second audit similarity-aligns the front, left-oblique and right-oblique 468-point
predictions, excluding the two profile views outside the model card's documented
yaw domain. The three-view consensus explains 90.8% of retained exterior depth
variance. Its nose-tip depth standard deviation is 0.33 px; the tested lip points
are 2.28–3.33 px. The consensus still predicts substantial remaining protrusion:

| Landmark | Remaining camera-depth change |
| --- | ---: |
| Nose tip 4 | -0.099921 |
| Nose base 2 | -0.043124 |
| Upper central lip 0 | -0.046368 |
| Lip 13 | -0.019691 |
| Lip 14 | -0.010778 |
| Lower lip 17 | -0.025603 |

These are learned relative predictions affinely tied to the current generic
surface, not scan truth.

## Falsification

Applying the fixed direction to the current surface improves the left profile
but immediately worsens the right. At only 1% strength, the original-camera
means move from 3.624/4.923 px to 3.566/4.995 px. Replaying after the protected
profile-camera correction reduces but does not remove the conflict:
3.619/4.900 px becomes 3.607/4.932 px.

An unconstrained two-scalar camera/depth solve asks for depth strength 0.204 and
pushes camera scale to its 1.2 bound, but its frozen direction fails from the
first step. The direct constrained solve terminates at depth strength
`7.4e-14` and unchanged camera scale 0.76: numerically zero.

The multi-view prior audit is `TECHNICAL_CHECK_PASSED`; direct deformation of
the current lifted surface is `REJECT`. This does not establish that MediaPipe
depth is wrong. It instead exposes a bilateral conflict among the current
surface attachment, profile cameras and profile correspondences. Do not weaken
one side's guard or bake the front prior into identity geometry.
