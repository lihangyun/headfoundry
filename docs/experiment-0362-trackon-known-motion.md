# 0362 fixed smooth-view correspondence control

2026-10-26. One inference run, CPUFP32/four threads, same0356weights/config,
0357operator,0360coordinates,0361online update rule. Only new test variable is
camera motion rather than identical frames. No patient/medical input.

Owned0332scene: reproduce its exact RNG331rectangles/textures/noise and verify
all three anchor image arrays equal saved originals before inference. Preserve
anchors at frame0,6,12. Interpolate camera yaw sequence
[0,3,6,9,12,15,18,12,6,0,-6,-12,-18]degrees, pitch
[0,2.5,5,7.5,10,12.5,15,15,15,15,15,15,15]. Same original gains/biases at
anchors; linear interpolation between. Intermediate sensor noise uses separate
fixed seed362, not parameter tuning. Renderer-only geometry never enters model.

All original0332source-only96corner queries from raw-endpoints.npz, no old flow
matches/admission masks. Before inference intersect source and all13cameras;
score only points geometrically visible and within4px image margin in every
frame, require>=48. Freeze this mask before predictions; feed all queries to
model and record all outputs/visibility, no model-confidence pruning. Evaluate
per-frame native-pixel endpoint p95<=3px over that fixed visible population.
Known truth used only to define benchmark/evaluate, never to fit model/cameras.
This is an owned textured-rectangle control, not human skin evidence or2mm.

Preparation<=300s/2GiB; forward<=600s/4GiB; one fixed config and input set.
Stop on source reproduction failure, coverage, runtime/budget or endpoint gate
failure. No image/point/threshold/precision rescue; failed control prevents
patient execution and requires documented closeout before another route.
