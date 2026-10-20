# Experiment0268: distinguish missing long tracks from disconnected geometry

Date:2026-10-20. Registered before the numerical test. Whole15-minute window
starts10:24:44Z,ends10:39:44Z. No model,video,scan or reconstruction fitting.

0267 remainsREJECT under its complete contract. Its raw component covers
frames0..876;14 keyframes888..1040 are outside it. No sequential identity612
survives to1040,while612 direct candidates exist. Do not infer physical matches
or camera quality from those candidates. Do not restore/sweep DIS or LK.

Question:does lack of a track spanning the whole sequence necessarily make
joint camera/point estimation unobservable? Main variable is visibility-graph
structure,not another tracker. Bundle adjustment attaches a residual to an
observed camera/point pair,not necessarily a fully visible point:
[Ceres primary tutorial](https://ceres-solver.readthedocs.io/latest/nnls_tutorial.html#bundle-adjustment).
This is mathematical evidence routing,not permission to relax any physical gate.

One deterministicseed268 synthetic scene:five general-position perspective
cameras,30 asymmetric points in three10-point groups,visible in cameras012,
123,234 respectively. No point is seen in both first/last cameras. Unknown
shared logfocal,all point positions and cameras1..4 are represented. Fix camera0
pose and camera1 translation-x=.4 to remove the7DOF similarity gauge. Construct
the analytic local reprojection Jacobian;require full column rank at fixed
absolute singular-value tolerance1e-4. Compare it with symmetric differences
at1e-5 and1e-6;require maximum derivative disagreement<=1e-5,all positive depths
and proper rotations. Negative control:remove camera4 observations without
removing its parameters and require rank loss. Check global scale projection
invariance separately before fixing that gauge. No scene/seed/threshold sweep.

Success proves only a local synthetic counterexample to a claimed necessity.
It does not prove global convergence,noise robustness,actual identity/rigidity,
real camera3px,medical2mm or any head quality. A connected graph alone is not
sufficient. If positive,retain one small generic regression;otherwise archive
and remove exclusive failed code. Current real disconnected component still
needs independently verified inter-component constraints,not track relabeling.
No Ceres dependency is installed;use existing NumPy/OpenCV and independent code.
