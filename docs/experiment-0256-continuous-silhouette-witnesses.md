# Experiment0256: continuous per-ray feasibility witnesses

Date:2026-10-20. Registered before new optimization.
Status:REJECT for continuous-witness unknown-pose recovery.
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

## Executed bounded outcome

Exact pre-result producer/protocol recovery:Git09b0e23. Preparation exports
only frozen native masks/2D contours/samples;source pixels match0254 exactly.
Fresh fit worker's STL/private-source denial checks pass. No oracle arrays are
available there. The eleven procedural interval/bilinear/pose/dependency controls
pass;the finite-difference sparsity check validates the declared toy fixture,
not a general formal proof for arbitrary code.

One10.945s process exits0,with8.055s inside fitting. TRF reports xtol termination
after47 solver nfev/41 njev and744 actual residual calls (including finite
differences). No retry or budget extension occurs. Raw mask RMS falls
3.148524->.129130px;final maximum remains4.635638px. All target witness-depth
barriers are zero,but original polygon coherence is.9860026042,below.99.

The solver success flag is a **step-tolerance stop**,not proof of a near-stationary
or global solution:reported optimality610.348273 is far above gtol1e-8. Do not
claim convergence merely because the numerical API reports success. A low
image-distance cost does not override the independent camera checks.

Post-termination evaluation uses every same original point and one global
angular-scale gauge. Every final view fails3px;five regress from initialization:

| View | Fixed visible points | Initial p95 px | Final p95 px | Final rotation error deg |
|---|---:|---:|---:|---:|
|front|2355|3.180587|3.168551|0.000000|
|yaw-10|2306|15.563537|19.803494|8.930611|
|yaw+10|2343|15.236549|23.351503|10.443567|
|yaw-30|2205|23.835696|23.989603|11.270415|
|yaw+30|2223|24.371535|28.076385|13.083884|
|pitch+10|2003|14.671897|15.948450|6.422386|

Final focal1497.7601px remains near the1500px initial guess,not the1083.2579px
fixture truth. Evaluation-only scale.1205419865 is shared by all final views;
no per-view alignment/reflection or point deletion. All13435 point-view samples
per stage remain. Proper rotations/original-point cheirality pass;independent
OpenCV projection replay is<=2.047e-12px. Actual source-only initial/final clay
panels with native residual arrows were inspected;they are not new head outputs.

## Enforced exit and next evidence requirement

RecipeREJECT. Execution/mathematical controls passed,but reliable unknown camera
pose did not. Faster residual minimization and smaller loss are not improved
camera/head accuracy;front's tiny numerical change still fails its own gate.
Do not promote a PARTIAL_SUCCESS or move this result to real reconstruction.

**Close this silhouette-only unknown-pose attempt family now.** No next distance
transform,loss/weight,sampling,depth prior,solver/tolerance,multi-start or added
iteration variant.0254 is retained solely as successful known-motion evaluation
math/fixture;its conditional pass is not unknown/real-camera acceptance.
This does not prove all silhouette theory impossible or uniquely identify the
failure cause. It establishes that these bounded no-texture/no-prior recipes
do not provide trustworthy cameras on this clean rigid source-mask regime.

Before further modeling,require genuinely independent material correspondences
or justified motion/shape information,not more reduction of this silhouette
loss. Investigating their availability in the already authorized video remains
in scope;no extra capture,source-scan inference or lower gate is silently assumed.
No case002/bone content,real-video inference,training,upload,head/texture/default
change or final quality acceptance occurs here. Full objective remains open.

## Retirement

Source recoverable at09b0e23. Preserve compact local reports,full trace,sanitized
2D input/control hashes and two bounded source-only projection panels;remove
exclusive0256 runner/raw outputs/cache before a different route. No package,
model or framework was added,so none needs removal. Keep originals,0254 math/
masks/0230 samples,shared tests and unrelated0207 draft. An archived failure is
not authorization to restore this solver or call its latent depths a head.

Actual closeout:992,009byte private evidence archive,CRC verified,SHA256
`f0012e363c3756642918fbb8312288985dc134b59cdb7ae56d4b9f37d77dc3dc`.
Remove14 raw files totaling1,385,428bytes plus the exclusive runner after
terminal-process/resolved-path/non-symlink checks. No exclusive cache/live
caller remains. Source recovery matches the executed producer hash;ten protected
input/consent/intake hashes and retained0254 masks/0230 archive remain exact.
131 shared tests pass in4.776s;Git whitespace check passes. Byte counts are
logical file sizes,not independently measured free-disk gain. No new package
or framework needs uninstalling. Compact numeric/review evidence remains local.
