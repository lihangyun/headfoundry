# Experiment 0157: full paired-target identity fit

Status: mapping/solver `TECHNICAL_CHECK_PASSED`; subject candidate and neural
training promotion `REJECT`.

This experiment transfers all 82 paired CC0 neutral controls through the
existing current-mesh mapping, subdivision and closed-patch construction. Each
signed coefficient uses its actual positive or negative target rather than a
false single linear direction. Cameras and the experiment-0132 source mesh stay
fixed.

The first central-difference fit is dominated by the more numerous frontal and
oblique samples: those improve while both profiles regress, so no nonzero scale
passes. The second run changes only evidence weighting, giving the bilateral
profiles equal aggregate influence. It selects a safe 0.35-scale candidate.
All four outline means and both aggregate profile means improve; maximum
displacement is 0.01166, minimum area ratio is 0.654 and no triangle reverses.
Seven of eight protected oblique eye errors improve; one regresses by 0.083 px,
within the predeclared 0.20 px experimental tolerance.

The independent interleaved-row audit rejects the apparent gain. Left held
profile error worsens from 4.247 to 4.643 px and right held error from 4.387 to
4.526 px, even though the fitted left rows improve strongly. Exact Blender
overlays and five-view clay comparison show no confidently visible identity
improvement. The mapper, signed control evaluation and solver are
`TECHNICAL_CHECK_PASSED`; the subject candidate and default/visual promotion
are `REJECT`.

Training a neural decoder on the same 82-control samples cannot add identity
capacity outside this rejected source manifold, so neural training is also
rejected at this gate. The next route needs either richer commercially usable
3D identity data or image-derived subject geometry with genuinely independent
multiview validation; more optimization of the same controls is not evidence.
