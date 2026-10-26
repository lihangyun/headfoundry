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

## Actual result

Preregisteredf3a4631; one forward run, no retries. Preparation15.844s /
284921856bytes verified-age process-tree peak. All three anchor image arrays
exactly match0332;96source corners,90geometrically visible across all13frames.
Frozen input archive SHA256:
7530a914000d6928c81b15d16427cb57649e70d931be1173fa9176a14bae81e1.

Inference45.469s /812318720bytes peak. All13actual feature/track forwards
completed. Native endpoint p95 by frame in pixels:
[0.690859,1.325981,1.238681,1.332564,1.267323,1.322763,1.302822,
1.396594,1.347118,1.272691,1.371948,1.427815,1.590252].
Every frame passes the preregistered3pxendpoint control; no confidence pruning.
Evaluation0.484s /46620672bytes.167shared tests pass9.051s.

TECHNICAL_CHECK_PASSED for owned smooth-view endpoint tracking only. The
model's result has not yet been used to estimate/calibrate a camera; no focal,
cheirality,held-view camera,head or medical2mm success is claimed. This textured
rectangle domain is not evidence of human-skin performance. Loader report's
model_forward=NOT_RUN describes its strict-load substage; infer.log separately
records completed frames0..12 and predictions.npz preserves their outputs.

Evidence at assets/private/trackon-motion-0362: inputs/truth fixed before
inference,prepared identity,96point predictions/visibility,all endpoint errors,
fixed90point mask,result and stage logs/receipts. Successful fixture retained.
Next gate: camera estimation from predictions only, with scene geometry/K/poses
held for independent evaluation; do not initialize from benchmark truth or
promote directly to patient head fitting.
