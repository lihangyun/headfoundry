# 0361 first complete forward: static owned image

2026-10-26. Preregister before first model forward. Main variable is the newly
admitted Track-On2 inference implementation, fixed CPUFP32/four threads,
0356checkpoint/backbone/config,0357operator,0360independent cell centers.
Use unchanged owned0332view-0.png twice,48fixed queries on8x6regular grid
within50pixel margins of the native image. Do not tune image/points/thresholds
after results. All48points included; report visibility without pruning.
Use trainedM24weights then upstream memory_extension72 as fixed test config.
Use explicit query initialization/grid_sample and online frame/point-memory
updates, excluding stock predictor/evaluator/NCgrid helpers.

Checks: full strict state loading; two actual feature/track forwards; finite
outputs/shapes; report every point's native-pixel absolute source-query error
and repeated-frame drift. Static-identity gate is each frame p95<=3px, same
camera pixel requirement, not proof of cross-view/3D or medical accuracy.
Two identical images are NOT a multiview physical reconstruction benchmark.
Budget600s/4GiB verified-age process-tree peak. Stop on resource/runtime/numerical
failure or failed static gate; no parameter/offset/precision or confidence rescue.
Engineering errors may be diagnosed, not labelled a measured physical failure.
If identity fails, no patient/model rerun without resolving and closing this test.
Owned inputs/evidence only; no new downloads, patient files or training.
