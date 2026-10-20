# Experiment0255: remove known relative rotations from silhouette capacity

Date:2026-10-20. Registered before pose optimization.
Status:REJECT for the bounded16-parameter unknown-rotation recipe.
Previous0254 is concrete progress:known-rotation focal capacity passes,source
and independent projection controls unchanged;it does not recover real cameras.
Use ponytail's existing-code/numerics minimum and CAMERA diagnostic scope only.

## Single changed prerequisite

Reuse0254's exact6 transparent source masks,all contours and512 native source
samples per view,complete depth-interval unions,one-pixel erosion and unweighted
mean coherence. No new masks/renders,regions,offsets,sampling,texture,shape or
point matching. Only primary variable:relative rotations are now unknown.

Optimize15 yaw/pitch/roll parameters for the5 non-reference cameras plus one
shared focal. Reference camera rotation diag(1,-1,-1) fixes the global frame;
it is not supplied relative-pose truth. Centered principal point(360,640),zero
skew/square pixels and common translation(0,0,1) remain model assumptions.
The latter is a fixed-pivot/unit-radius rotational-object model,not arbitrary
real six-DoF motion. No claim of human turntable rigidity follows.

Use `look_at_origin` on the unit center direction from yaw/pitch,then camera-Z
roll. All3 angles are free for each non-reference view. Fixed coarse initial
degrees (yaw,pitch,roll),by immutable view order:
(-15,2,3),(15,-2,-3),(-40,2,-3),(40,-2,3),(0,15,3).
Initial focal1500px. These are broad manually declared view-class hints,not
blind image pose initialization and not read from true camera matrices.
Same bounds for every non-reference view:yaw[-80,80],pitch[-40,40],roll[-30,30].
Focal[400,4000]. Parameters are log(f/1000) and angles/45deg.

One bounded Powell solve,xtol1e-3,ftol1e-5,maxfev400,maxiter10,900s cost budget,
930s external watchdog. No multi-start,parameter-order,bounds,solver,precision,
per-view or tolerance rescue. Every evaluation records parameters and coherence;
best checkpoint selection uses only coherence,never true geometry/projection.
Normal successful termination is required;budget exhaustion is not convergence.

## Keep true3D out of the pose worker

Preparation validates original rights/hash provenance and0254's successful
fixture,then exports a separate NPZ containing only2D contour vertices and
source pixel samples. Assert every sample identical to0254. No true K,R,t,
point arrays,visibility,metric coordinates,errors or optimized0254 focal enter
that file or worker configuration. Source view names are audit labels only.

A fresh fit process receives sanitized2D data and fixed initial constants.
It never calls the oracle loader. A Python open-audit guard refuses every STL
and private-repository asset outside its own experiment directory;verify a
denied oracle/absent-STL read before fitting. This audits our Python code paths,
not a security sandbox or defense against hostile/native bypasses. No source
scan,case002,bone,FLAME/model/landmark asset or real video is conditioned into fit.

Only a separate post-termination evaluator reads0230's immutable material
points,true K/rotations/visibility. It evaluates both fixed initialization and
final selected cameras on **every originally visible point in each view**.
To compare arbitrary unit-radius output gauge with the source,one analytic
whole-scene scale f_truth/(6*f_recovered) applies to all normalized source points,
the same angular-scale convention as0254. This is an oracle evaluation gauge,
never inference feedback,per-view alignment or deformation. Report its value,
raw focal error,rotation errors and exact formula;do not hide focal uncertainty.

Every final view must retain its full fixed visible population,p95 reprojection
<=3px,proper rotation and all-point positive depth;independent OpenCV replay
<=1e-5px. Require coherence>=.99 and successful termination too. No validation
point deletion,per-view selection,scan-driven coefficient fit or metric feedback.
If any required camera fails,recipeREJECT before real transfer/head fitting.
Even a complete pass proves only this constrained unknown-rotation source-mask
capacity,not arbitrary six-DoF pose,real segmentation/rigidity,2mm anatomy or
actual full-head likeness. No full objective is waived or called complete.

## Controls,evidence and exit

Require existing interval/cube/projection controls plus proper unit-radius
pose construction,+Y-up,invalid-input and worker denial controls. Hash-lock the
sanitized NPZ,0254 helper,producer,protocol and copied mask metadata. Inspect
actual source-only initial/final projection panels after evaluation;labels must
say supplied scan/not reconstructed head. No training,upload,new package/model,
case002/bone bytes,default changes or second optimization.

If failure,retain compact reports/trace/sanitized-control identity/few review
images and Git producer recovery point;remove0255 exclusive runner/raw outputs
and caches after CRC/hash verification,shared regressions and focused commit.
Keep0254's successful math/fixture and all originals. A failed joint unknown-pose
recipe must not be rescued by claiming0254's conditional pass proves real pose.

## Actual single-run outcome

Exact executed pre-result producer/protocol:Git9985fa1. Preparation exports
only six2D contour arrays and a6x512x2 sample array;all samples are bit-identical
to0254. Independent schema audit confirms seven finite float64 image-coordinate
fields,no K/R/t,visibility,metric point or error arrays. Fresh worker guard
refuses source-oracle and absent-STL reads before fitting. Its input SHA256 is
`4fab2196cc87aa39af131e0751676392161d9560cdb6ac786b35c76b4cf22b2d`.

One605.852s fit completes400 evaluations and exits0 with an explicit **unsuccessful
optimizer termination**:maximum function evaluations exceeded. This is successful
process execution,not convergence. Best coherence rises.7356770833->.888671875,
still below.99. The cost-only best checkpoint happens to be evaluation400;
no point errors were available to its selection. No second solve is launched.

A separate evaluator starts only after the worker's terminal exit. Every final
view misses3px and regresses from the fixed initialization:

| View | Immutable visible points | Initial p95 px | Final p95 px | Final rotation error deg |
|---|---:|---:|---:|---:|
|front|2355|3.180587|3.612458|0.000000|
|yaw-10|2306|15.563537|30.709905|14.003506|
|yaw+10|2343|15.236549|33.236186|14.365938|
|yaw-30|2205|23.835696|81.472305|41.343536|
|yaw+30|2223|24.371535|38.536649|17.975936|
|pitch+10|2003|14.671897|32.492195|13.333334|

Final focal1585.3761px;one evaluation-only source scale.1138802177 applies to
all views,versus initial.1203619869. No similarity/reflection/per-view adjustment
is fit to rescue these numbers. All rotations/positive depths pass,and independent
OpenCV projection agrees within5.685e-13px across both stages. Numerical replay
therefore does not explain away the failed cameras. All13435 sample-view pairs
per stage remain;none is filtered after evaluation.

Actual initial/final6-view projection panels were inspected. They show the
unchanged **supplied scan**,native-pixel red residual arrows and green observed
points,not a reconstructed or improved head. The final panels visibly regress.
Read-only saved-trace audit finds66/399 adjacent equal scores,185 distinct
scores and a1/3072 count quantum. This describes quantization,not proof that
flatness is the sole failure cause. No perturbation sweep or refit follows.

## Decision and limits of the negative result

Reject this16-parameter/binary-coherence/Powell/coarse-seed/400-evaluation recipe
before actual-video transfer or head fitting. **Do not increase its iteration
budget,change initial seeds/bounds,reduce pose freedoms,or alter pixels/offsets
to rescue it.** Improving a fitting score did not improve independent cameras.
0254 remains a successful **known-rotation** mathematical fixture,not an unknown
camera initializer;the present result must be shown beside its conditional pass.

The true cameras already give coherence1 in0254 and are representable here:
there is a valid known solution. This run neither reaches the global optimum
nor proves every silhouette method incapable. It proves the registered recipe
has not recovered trustworthy unknown poses,even on clean rigid source masks.
A future approach needs a materially different justified observation/motion/
numerical mechanism and new bounded registration,not another numerical sweep.
Do not infer real-video rigidity,actual millimeter accuracy or visual acceptance.

## Retirement

Before any new route,archive compact reports,complete trace,exact sanitized2D
input/control identities and the two bounded source-only projection panels.
Remove0255's exclusive runner/raw outputs/cache after archive verification.
Recover source from9985fa1;original masks/0230 samples/shared0254 math and tests,
authorization,case002,bone and unrelated0207 draft are intentionally preserved.
No package/model/framework was installed,so none needs removal. This does not
complete or pause the full head goal;it prevents transferring another failed
camera prerequisite into a misleading head result.

Actual cleanup:private archive941,675bytes,CRC checked,SHA256
`b1872b8e9c1dde96c822d72704eaf6cd0c900dc9fe4543da9eae85e1cca27220`.
After confirming terminal exit and resolved non-symlink target,remove16 raw
files totaling1,174,795bytes plus the exclusive tracked runner. No exclusive
Python cache or live caller remains. Git source recovery matches the executed
producer hash. Ten protected input/consent/intake hashes and successful0254
masks/0230 archive remain exact.131 retained tests pass in4.820s and Git
whitespace check passes. The archive preserves compact numeric/review evidence,
not a new distributable head or permission to revive the rejected solver.
