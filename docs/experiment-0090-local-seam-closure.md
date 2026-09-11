# Experiment 0090: compact seam closure trial

Status: both nonzero candidates `REJECT` for promotion.

Primary variable: closure fraction for the two existing uncertain seam samples.
Keep the experiment-0079 coupled head/cameras fixed as the source. A compact
smooth radial displacement field with radius 0.12 template units moves the two
barycentric samples toward their midpoint; solve its two coefficients using
the actual triangle weights, not abstract center coordinates. Verify the full
field would bring the samples together numerically, then test only 0, 0.25,
0.5 fractions. This is an explicit hypothesis test, not anatomical lip pairing.
4233 vertices outside support remain exactly unchanged. No topology welding.

| Diagnostic | Source | Quarter closure | Half closure |
| --- | ---: | ---: | ---: |
| Sample separation, template units | 0.024615 | 0.018461 | 0.012307 |
| Maximum movement | 0 | 0.006047 | 0.012095 |
| Minimum area ratio to immediate source | 1 | 0.862962 | 0.732414 |
| Reversed triangles | 0 | 0 | 0 |
| Left whole profile MAE, px | 3.589129 | 3.634597 | 3.678431 |
| Right whole profile MAE, px | 7.249347 | 7.217162 | 7.196348 |

At quarter closure both samples remain ray-visible. At half closure the lower
sample becomes occluded in all three frontal/oblique cameras, with surface gaps
0.00708/0.00903/0.00966 template units. Triangle orientation alone does not detect
this loss of observation support; it must not count as a better fitted seam.

Actual enlarged frontal and bilateral profile clay crops were rendered and
inspected alongside the photos. The opening does not become a natural closed
lip contour; angular anatomy persists and the stronger deformation begins to
hide the lower support. Quarter closure also regresses the left profile and
does not provide convincing visual improvement. Do not increase the fraction
or identify the existing two samples as opposing lip boundaries without new
anatomical evidence. Collision freedom was not established.

The next closure implementation requires explicit upper/lower lip-rim geometry
and a compatible rest configuration, not attraction between detector-derived
surface hits. The tests above reject this particular field, not all possible
closure models. No candidate/source/camera promotion, no acceptance claim.
Private `seam-closure-v1` retains three actual OBJs, report and enlarged rendered
comparison. Source, camera, support hashes and local consent were verified.
Public production code remains unchanged; validation is the actual field
identity/support check, triangle checks, ray checks and inspected render.
