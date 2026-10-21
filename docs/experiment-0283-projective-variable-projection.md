# Experiment0283: projective variable projection before metric camera recovery

Registered2026-10-21T12:39:46Z,before implementation/controls/estimation. Whole
2400s includes implementation,one control,at most one actual cohort,and cleanup.
0282 is closed/cleaned at2dab753;no accepted head exists. No old affine metric
eigenvalue,ALS count,mask,frame,focal bound or acceptance threshold is adjusted.

Evidence:0282 recovers exact synthetic perspective cameras after fixing parity,
but actual affine fitting has16.77px training residual and an indefinite3x3metric.
That does not distinguish perspective approximation from bad material tracks.
Main variable:estimate full projective cameras BEFORE metric upgrade,instead of
requiring an affine metric initializer. This is not another parity/solver sweep.

Mathematical motivation:[InitFree BA controlled study,2026](https://arxiv.org/html/2608.18028v1),
OSE residuals/variable elimination and dual-quadric upgrade. Its low-loss versus
metric-quality warning is essential. Independent NumPy/SciPy implementation,
not a reproduction of its C++ solver or empirical performance. No external code,
framework,model,weight or dataset is installed. No claimed guaranteed convergence.

## Fixed inference contract

Normalize image centers by subtracting(360,640),dividing1500. Estimate full3x4
projective cameras with pOSE:OSE residualP1:2*Xh-(P3*Xh)*uv plus affine residual
P1:2*Xh-uv,weights sqrt(.95)/sqrt(.05). Eliminate each3Dpoint by linear least
squares with Xh4=1. Optimize remaining cameras by analytic reduced gradient
(envelope theorem),SciPyL-BFGS-B,maxiter400/maxfun1000,ftol1e-12,gtol1e-8,
180s per cohort. Camera0 fixed to affine projective gauge[[1,0,0,0],
[0,1,0,0],[0,0,0,1]]. Other cameras start normal(seed283),first2x3 entries
sigma.1,third-row first3 sigma.01,third constant1,and observed training per-view
mean as first2 translations. This is a fixed generic prior,not true pose/shape.
Check20 deterministic reduced-gradient coordinates before any optimization.

One subsequent projective reprojection BA,soft_l1 scale2nativepx,max_nfev60,
180s. Fix camera0,one largest-magnitude parameter per other camera for camera
scale,and Z coordinates of four points selected by pivoted QR of XhT for the
remaining projective gauge. No scan or shape penalty. Report finite/depth/rank,
all training residuals and optimizer state,not just surrogate cost. No restart.

Linear metric upgrade:four zero-skew/centered-principal/square-pixel constraints
per camera on symmetric4x4dual absolute quadric. SVD solve,positive-trace sign,
require top3eigenvalues positive,always project to rank3 using those eigenpairs;
fourth eigenvalue/discarded Frobenius norm are explicitly reported,not hidden.
Unlike0282's3x3affine metric,this mathematical object has a required null mode.
Construct H from three square-root eigenvectors plus the null eigenvector.
Try exactly two signs of the last H column;choose by training positive-depth
count,tie->positive,BEFORE held scoring. RQ decomposition yields proper metric
cameras;median of all fx/fy gives one shared initialf. Report intrinsic mismatch;
it cannot pass merely by being finite. Reject invalid/nonpositive training
geometry orf outside(400,4000),no eigenvalue clamp/threshold search/rescue.

One original sparse Euclidean BA(initialf now from metric upgrade),otherwise
unchanged0280loss/gauge/60evaluations/180s. Only after final camera freeze score
all whole held identities with unchanged leave-one-target-view-out scorer.
Require convergence,positive/proper cameras,trainingp95<=3px,and>=30held rows
per view,zero invalid/weak rays,global AND every-viewheldp95<=3px. No pruning,
held selection,semantics-as-material or medical geometry in estimation.

## Immutable controls/data and stopping

First exact0280seed280 synthetic control:600points/five known cameras,each point
missing one view,(id//5)%5;whole-ID id%5holdout. Estimator receives only2Dtraining
observations,never true pose/3D/scale/relative rotation. All480untouched held
predictions mustp95<.1px,negative17*view_index^2xoffset must fail3px. Software
control failure stops before patient input. Gradient max relative error<1e-4
(absolute<1e-6 for nearzero coordinates),no tolerance retuning.

If control passes,shared rights/hash validation of only originalcase001video,
then exact0267archiveSHA54aa2b303e4fa6f0599628f677bf359e4125dccd1df867ea70f8b9e19154c612.
Same74frames0..876stride12;train id%5!=0/>=3,held id%5==0/>=4;all59448rows.
No raw frame re-extraction,scan,bone,case002,neural training or upload. Track
physical identity remains unverified;even a numerical pass is at most
PARTIAL_SUCCESS,not head/surface2mm/visual acceptance. Missing888..1040 stays
unresolved. No formal head fit before actual camera/material gates.

Implementation<=900s,control<=600s,actualpOSE/projectiveBA/EuclideanBA<=180s
each,held<=120s,whole2400s. One configuration,one worker,ordinary pre-estimate
interface fixes disclosed. Any scientific failure stops without another seed,
alpha,loss,iteration,rank,precision,point/frame/threshold sweep. Preserve compact
reports/controls/hashes/Git recovery;remove failed exclusive runner/raw output/
bytecode before another route. Original materials/rights/successful fixtures,
common runtime/defaults and unrelated0207 stay. Verify/tests/local cleanup
commit,no push and no fabricatedACCEPT.

## Actual result:projective fit passes training,metric controlREJECT

Executed7f3eade. Syntax/AST checks prove control,patient and held scorer unchanged
from4dff222;Euclidean bundle only accepts the metric-upgrade initial focal.
One29.641s worker. Reduced-gradient check20coordinates:maximum absolute
3.99434e-9,relative2.55969e-7. pOSE stops at its fixed400iteration limit,
433evaluations,objective.00213842349,28.968s;no convergence claim. One subsequent
projective BA converges in8evaluations/.641s,trainingp954.0709132e-11px,zero
nonpositive denominators. These are training/numerical facts,not held geometry.

Linear metric upgrade fails its required three-positive-mode condition. Eigenvalues
[-.00467916223,-.00172175906,-.00026585496,1.00038785526];no clamp or alternative
is tried. Its two smallest constraint singular values are2.66279e-13 and
3.64928e-16,next.122470. Only the last singular vector was used by this frozen
implementation. Thus linear ambiguity is a specific issue worth testing rather
than treating a tiny projection error as true metric recovery. No Euclidean BA,
held/negative score,patient manifest/observations,medical geometry or head run.
Overall control/inferenceREJECT;camera/head/medical accuracy remainsUNVERIFIED.

### Read-only analytic diagnosis,not a repaired estimate

The known control generator has P_i=[R_i|t],t=(0,0,10),normalized trueK=I.
For Q0=diag(1,1,1,0),P_i Q0 P_iT=I. But rank1Q1=diag(0,0,0,1) also gives
P_i Q1 P_iT=diag(0,0,100). Both exactly satisfy the four selected linear
zero-skew/centered/square-pixel constraints for all rotations. Direct independent
arithmetic checks maximum residual below1e-15. Only Q0 is rank3 with a valid
nonzero focal camera metric. A single linear null-vector is therefore not a
sufficient upgrade algorithm on this control. This analytic oracle diagnosis
uses known synthetic cameras only,after failure;it is NOT fed to the estimator,
does not rerun it,does not prove an actual-video solution or change0283REJECT.

A future separately registered algorithm may enforce rank3 within the ambiguous
linear subspace and select using training-only camera constraints. It must not
choose by known synthetic focal/pose,held observations or medical geometry;no
new attempt starts until this route is archived,cleaned,verified and committed.
