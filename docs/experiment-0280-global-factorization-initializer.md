# Experiment0280: global missing-track factorization initializer

Registered2026-10-21T07:52:00Z,before controls or candidate geometry. Budget1500s
including implementation,one control,one actual solve,evidence,cleanup and commit.
0279 is closed/cleaned atf2ab202. No accepted head or patient camera exists.

## Evidence,hypothesis and single variable

0267 preserves short native-video tracks across74 connected keyframes,including
both profiles,but does not establish physical identities.0275's pairwise-F/global
pose pipeline returns zero models.0268 establishes only local observability.
Hypothesis:a joint low-rank affine measurement fit and metric upgrade can supply
a usable global initialization without estimating pairwise fundamental matrices.
The main variable is this initializer/estimation mechanism on unchanged0267 data.
No restored tracker,neural model,source rendering,scan prior or downloaded runtime.

Mathematical motivation:[Tomasi/Kanade1992 official publication record]
(https://publications.ri.cmu.edu/shape-and-motion-from-image-streams-under-orthography-a-factorization-method).
Independent NumPy/SciPy implementation,not copied publisher code. Orthography
is only an initialization approximation;its residual cannot pass the final
pinhole camera gate. Perspective,missing observations,nonrigidity and drift can
invalidate it. Failure rejects this fixed initializer,not every rigid model or
the video's theoretical reconstructibility.

## Immutable data and method

Verify0267 archive SHA54aa2b303e4fa6f0599628f677bf359e4125dccd1df867ea70f8b9e19154c612.
Use only observations.npz,frames0..876/stride12,stored pixel centers unchanged.
Train whole identities id%5!=0 with>=3 observations;held id%5==0 with>=4.
No held observations enter initialization,metric upgrade,calibration or BA.
Reject duplicates/nonfinite/insufficient per-view data. Validate onlycase001 video
rights/hash using shared manifest boundary. No scan,bone,case002 bytes opened.

Center observed coordinates per view,zero-fill missing centered entries,rank3 SVD
initialize;50 fixed alternating least-squares point/affine-camera updates with
translation and prediction-preserving gauge normalization,no residual pruning.
Solve homogeneous six-variable metric constraints(row orthogonality/equal norm).
Require a positive-definite metric,without eigenvalue clamping or sign-branch
search;closest scaled orthonormal rows give proper rotations. Canonical positive
trace metric sign only. Fail if singular/indefinite or points have invalid depths.

Initialize sharedf1500,principal(360,640),zero distortion,positive depthf/scale.
One sparse perspective BA:free training points,cameras1..V-1 and logf in(400,4000),
camera0 fixed and one maximal-distance coordinate of point0 fixed for scale.
SciPy least_squares,soft_l1 scale2,max_nfev60,x_scale=jac,180s wall cap;no scan
or shape prior. Require optimizer success,proper finite cameras,all observed
training depths positive,trainingp95<=3px. No precision,iteration,focal,mask,
rank,frame,threshold or identity sweep after a failed score.

## Independent control and held protocol

Before actual data:seed280,600 asymmetric random3D points,5 cameras(yaws
-35,-17,0,19,37degrees,pitches-8,5,0,-4,7),f1500,depth10. Each point omits exactly
one view via(id//5)%5,independent of held id%5;no complete track. Same initializer/
BA must give heldp95<.1px and proper positive-depth geometry;otherwise stop before
patient geometry. Negative held observations shifted17px must fail3px. This is
implementation evidence,not patient or medical accuracy.

Freeze fitted cameras. For each held identity and every observed target view,
triangulate by unweighted DLT from ALL OTHER observed cameras,then score that
untouched target. No target used as anchor,no endpoints omitted,no held BA or
outlier pruning. Missing/rank-deficient/negative-depth/weak-ray(<1degree maximum
anchor separation) cases count as failures. Require>=30 held rows in every view,
all finite positive predictions,global AND each-viewp95<=3px. At most
PARTIAL_SUCCESS geometric consistency on unverified track identities,never full
physical camera/medical/visualACCEPT. Full head and2mm surface gates unchanged.

Implementation<=600s,control<=180s,actualALS<=120s,actualBA<=180s,evaluation<=120s;
whole1500s. One scientific attempt,no hidden rescue. Ordinary interface errors
before estimates may be repaired with disclosure. Failure:preserve compact
reports/observational errors/hashes/Git recovery,remove exclusive runner/output/
bytecode,verify protected originals/shared tests,focused local cleanup commit
before another route. Shared environment/production defaults and0207 stay.

## Actual result:controlREJECT,patient geometry not executed

Executed source4dff222. One process completes in2.015s.480 training/120 entirely
held identities and480 leave-one-view-out predictions are scored. The affine
trainingp95 is3.783626px. Metric eigenvalues(.284188,.469216,.836184) are positive;
this establishes no perspective recovery guarantee. One perspective solve reports
ftol convergence after48evaluations,butf3999.999999998 nearly saturates the4000
bound,trainingp95 is5.119345px and independent heldp95 is6.857703px. Per-view held
p95 is8.946314,5.249052,3.180540,5.255673,9.883681px;all96rows/view remain counted.
No invalid/negative-depth held point is removed. Wrong-observation control is
168.948342px. Proper rotations/positive depths and optimizer success do not pass
the registered<.1px software-recovery control or actual3px target.

Stop before loading0267 observations or estimating patient cameras. The quoted
errors are synthetic control pixels,not actual video/medical millimeters. No
patient geometric error,head,scan comparison or visual improvement is measured.
No focal/iteration/reflection/threshold rescue. Local minima,approximation and
depth-handedness ambiguity are plausible mechanisms,not uniquely established
causes. This rejects the fixed initializer implementation,not global geometry
in general. A future claim needs reliable unknown-pose recovery on a complete
independent control;do not proceed just because a metric matrix is positive.

Five protected hashes remain unchanged,including selected originalcase001video,
authorization/input manifests,successful0230fixture and unrelated0207. They are
hash checks only,not scan-derived estimates;case002 is not opened. Worker never
reaches its patient manifest/archive branch. No model/environment is installed.
Closeout preserves the small report/control-camera evidence and source recovery,
then removes the failed exclusive runner and raw output duplicates.
