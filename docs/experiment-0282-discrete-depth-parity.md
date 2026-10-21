# Experiment0282: explicit depth-parity alternatives,training-only choice

Registered2026-10-21T12:22:30Z,before any replay or new solve. Whole2400s
including implementation,one synthetic control,at most one patient cohort,
evaluation,cleanup/tests/commit.0280 closed atd8ccc39;0281 is read-only evidence.
Goal remains the actual-video editable head and unchanged3px/2mm/visual gates.

## Evidence and single structural variable

0281's archived cameras are.51..1.39deg from depth-reflected relative motion,
but43.9..145.3deg from true relative motion. This does not establish initial
branch or sole cause. It justifies explicitly representing the two discrete
affine-depth alternatives rather than repeating the canonical factorization.
Main variable:two algebraic parity candidates with training-only objective
selection. Not random restarts,focal/threshold/iteration tuning or model sweep.

Reuse our own0280 source4dff222 internally throughapply_patch,not a third-party
framework/model. Existing NumPy/SciPy only,no assets/environment/downloads.
Factorization,all50ALS updates,sparse BA objective/loss/60evaluation/180s cap,
f1500 initial/(400,4000) bounds,principal point,gauge,coordinate conventions,
all inputs/masks/whole-ID holdout and LOO scorer remain scientifically unchanged.
No source scan/bone/case002 data enters reconstruction. No uploads/training.

## Prospective branch construction and choice

Factorize training observations once. From (X,R,t) construct exactly:
0=(X,R,t);1=(S X,S R S,t),S=diag(1,1,-1). Array row convention X1=X S.
These have identical affine XY predictions and proper rotations but distinct
perspective depth. Check XY equality,properness and the involution before BA.
Save initial cameras/shape for diagnostic evidence,not a head output.

Run the same BA once per branch,in order0then1. Each gets the original180s/
60evaluation cap;no rescue of either branch. Record both optimizer states,
training objective costs,trainingp95/focal/depth/rotation diagnostics and times.
Eligible candidates require convergence,finite parameters/objective,proper
rotations and positive observed training depths. Choose the smaller optimizer
training cost(tie->0),before seeing any held observations. If none eligible,
stop. Camera0/one-coordinate scale gauge is independently fixed per branch by
the same existing rule. No true synthetic camera/point or held residual selects
a branch. Any training/held gate failure ends this recipe without a third start.

Only AFTER choice,score all eligible untouched whole-ID held observations via
the unchanged leave-one-target-view-out DLT scorer. Do not score/select loser
using held errors. All invalid/weak(<1deg)/negative cases count as failures;
>=30rows/view,global AND each-viewp95<=3px,trainingp95<=3px and broad focal/depth/
properness requirements remain. Success at mostPARTIAL_SUCCESS consistency,
not established physical identity,metric skin accuracy,full head orACCEPT.

## Immutable control,data and budgets

First exactly0280 seed280/600points/five known-camera control,missing(id//5)%5,
whole-ID id%5holdout. Choose only by training objective;then require480 held
predictionsp95<.1px,proper positive depth. The unchanged negative check uses
x offset17*view_index^2px(explicitly,not uniform17px),must fail3px. This tests
the new complete inference path,not known-camera-assisted initialization.
Failure stops before patient branch. No control camera/points guide actual data.

If control passes,validate only authorizedcase001 video through shared rights/
hash boundary. Read only0267 observations.npz from archiveSHA
54aa2b303e4fa6f0599628f677bf359e4125dccd1df867ea70f8b9e19154c612.
Frozen0..876stride12(74frames),train id%5!=0/>=3,held id%5==0/>=4,unchanged
native pixel centers,no filtering by residual. Missing888..1040 coverage remains
unresolved;0267 and0280 conclusions remainREJECT. No head fitting until camera
and physical-correspondence requirements genuinely pass;medical evaluation is
not reached merely by sparse numerical consistency.

Implementation<=600s,control<=420s,actualALS<=120s,two actualBA<=180s each,
held evaluation<=120s,all closeout<=2400s. Watch one worker,no duplicates.
Pre-register fixes only for ordinary pre-estimate interface errors;no silent
scientific replay. On failure keep compact reports/all training branch stats/
necessary initial-camera evidence/source hashes and Git recovery;remove failed
exclusive runner/raw outputs/bytecode,not common runtime or original evidence.
Verify protected originals/0207/shared tests/defaults and commit local cleanup
before another route. No push or false visual acceptance.
