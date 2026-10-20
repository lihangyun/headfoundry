# Experiment0256: continuous per-ray feasibility witnesses

Date:2026-10-20. Registered before new optimization. Status:UNVERIFIED.
Previous0255 made progress by rejecting and retiring an untrustworthy camera
recipe at884d1ea,not by improving a reconstructed head.

## Supported different mechanism

0255's binary count supplies only a1/3072 score quantum. Its saved trace has
66/399 adjacent equal values;higher counts accompany worse true projections.
That does not establish quantization as the sole cause. Test one materially
different numerical formulation:explicit ray-depth witnesses with continuous
outside-silhouette pixel residuals,instead of count maximization and Powell.
Do not revive0255's solver,increase its budget or alter its seeds/angle bounds.

The numerical formulation includes a compatible sparse least-squares solve;
this is not a causal ablation isolating optimizer from residual design. It is
one complete recipe test. The ray depths are temporary camera nuisance variables,
not a head mesh,template fit or accepted geometry. There is no new observation,
learned model,dependency,texture,training,service or real-video fitting.

## Frozen input,pose model and initial state

Use exactly0254's6 masks,all512 eroded contour samples per view,native pixel
centers and6 source view order. No crop,mask dilation,offset,threshold,pixel,
sample selection or contour simplification change. Preparation verifies masks
and sample equality against the successful fixture. Fresh fit input contains
only binary masks,2D contours/samples and hashes,no source coordinates,cameras,
optimized0254 focal,visibility or error arrays. Same Python private/STL denial
guard and post-termination oracle isolation as0255;not a hostile-code sandbox.

Keep the exact16 camera parameters,unit-radius/fixed-pivot assumptions,reference
diag(1,-1,-1),center(360,640),square pixels/zero distortion and initial1500px.
Same initial (yaw,pitch,roll) degrees:
(-15,2,3),(15,-2,-3),(-40,2,-3),(40,-2,3),(0,15,3).
All15 relative orientation variables remain free;same yaw+-80,pitch+-40,
roll+-30 and focal[400,4000] bounds. These are coarse hints,not blind pose.

Add one positive source-camera depth z per immutable source ray,all initialized
to1,log-depth bounds[log(.1),log(10)] in the fixed unit-radius gauge. Each
witness X=C_source+z*R_source.T*K.inverse*pixel is projected to all5 other
cameras. No true depth or scan surface enters fitting.

For each target mask,cache exact OpenCV L2 distance-to-foreground on native
pixel centers. Bilinearly sample this nonnegative field at each projected
witness;inside foreground is zero. Outside-image residual adds Euclidean
distance to the image rectangle to its clamped field value,never dropping a
ray. Target projection uses safe depth max(Z,.001),with additional residual
f*max(.001-Z,0) for positive-depth enforcement. This numerical barrier is not
an acceptance tolerance;independent original-point cheirality remains required.
Each ray/target has both residuals,unweighted linear squared loss,no robust
point rejection,depth regularizer,shape prior or per-view weighting.

One bounded SciPy TRF/LSMR solve,jac='2-point',sparsity for shared focal,
source/target rotations and the single source depth;max_nfev60,ftol/gtol1e-8,
xtol1e-6,x_scale='jac'. Record actual residual calls including numerical
Jacobian probes separately from solver nfev.180s fit budget,210s external
watchdog. No retries,alternate seeds,loss/field/scale/depth-bound sweep or
adaptive point deletion. Normal terminal state is the selected output;
budget-aborted checkpoint is diagnostic only and cannot pass.

## Unchanged independent gate and controls

After termination,one evaluator reads0230's original samples/K/R/visibility.
Use the same single all-view evaluation gauge f_truth/(6*f_recovered),not
per-view alignment. Score initial and final on every original visible point.
Need successful optimizer termination,original polygon-ray coherence>=.99,
all witnesses target-positive,and every original-view p95<=3px/proper R/
all-point cheirality/OpenCV replay<=1e-5px. Tiny distance loss alone cannot
accept a camera. No2mm anatomy,real-video applicability,full-head likeness,
physical scale or final mesh claim follows even from a conditional pass.

Before actual data require bilinear native-pixel/out-of-image fixtures,
proper pose/up/invalid input checks,a true zero-residual identity-view fixture,
positive-depth negative control and finite-difference proof that the declared
Jacobian pattern omits no numerical dependency. Retain0254's interval/cube
controls. Hash-lock producer/helper/inputs/pre-result protocol. Actually inspect
fixed initial/final supplied-scan residual panels;never present them as new heads.

If this continuous explicit-witness formulation also fails,close this attempted
texture-free silhouette-only unknown-pose family here. Do not add another
distance field,loss,window,solver,depth prior or multi-start numerical variant.
Keep successful0254 evaluation math,not a claim that unknown pose is solved.
Archive compact evidence and remove0256 exclusive code/raw outputs/cache before
another route under0250 policy. No case002,bone,original/default changes.

## API basis,not face-quality evidence

[SciPy least_squares](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.least_squares.html)
documents bounded sparse residual optimization and that max_nfev excludes
numerical-Jacobian calls. Installed SciPy1.18.1 is checked locally. The sparse
dependency pattern and witness equations are independently implemented here.
[OpenCV distance-transform documentation](https://docs.opencv.org/4.x/d2/dbd/tutorial_distance_transform.html)
is an API reference,not a face-reconstruction accuracy result. Neither source
establishes uniqueness of silhouettes or applicability to the real video.
