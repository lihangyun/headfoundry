# Experiment 0148: lower-face bilateral conflict audit

Status: read-only diagnostic `TECHNICAL_CHECK_PASSED`; geometry remains
`REJECT`; expression/pose explanation `UNVERIFIED`.

This audit replays the rejected experiment-0147 step at scale 0.05 and reports
every interleaved transfer sample separately. It changes no mesh, camera or
observation. White rings mark the existing photo readings, yellow marks the
baseline model, and green/red mark improving/regressing movement.

The right-side failure is not one isolated sample. Three consecutive lower-face
points regress: indices 6, 8 and 10 change by +0.030, +0.123 and +0.077 px in
absolute error. They span the subnasal/upper-lip/lower-lip region and share the
same signed direction. Two lower chin samples improve by 0.125 and 0.044 px.
On the left, four of five transfer samples improve; only the lowest tested row
regresses by 0.051 px. Visual inspection places the observations on the visible
photo contour rather than on hair, rear neck or an obvious disconnected edge.

The deterministic replay is `TECHNICAL_CHECK_PASSED`. The nonzero geometry
remains `REJECT`. The audit does not prove facial asymmetry or expression
difference, but it falsifies the simpler claim that one bad right-side point
alone caused rejection.

Next gate: represent small per-view mouth expression/pose as a nuisance variable
separate from neutral identity. A candidate neutral shape may be optimized only
after showing that the nuisance model explains the bilateral mouth conflict
without moving nose/chin evidence or improving a view through unconstrained
2D offsets. Do not bake one photograph's mouth state into asymmetric identity.
