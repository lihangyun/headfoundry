# Experiment0255: remove known relative rotations from silhouette capacity

Date:2026-10-20. Registered before pose optimization. Status:UNVERIFIED.
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
