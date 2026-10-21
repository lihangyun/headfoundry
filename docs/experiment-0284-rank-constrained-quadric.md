# Experiment0284: rank-three quadric pencil,not one arbitrary linear vector

Registered2026-10-21T12:50:20Z,before new upgrade/control/actual solve. Whole2400s
including implementation,one frozen-prefix control,at most one actual cohort,
evidence/cleanup/tests/commit.0283 cleaned/committed at1426957. Goal unchanged.

## Evidence and single variable

0283 fits projective control trainingp954.071e-11px,but its last linear singular
vector has only one positive eigenvalue. Its actual control cameras analytically
admit both rank3validQ0 and rank1invalidQ1 with zero linear residual. This is a
structural ambiguity,not evidence to increase optimization iterations or relax
actual3px/2mm/visual gates. Main variable:enforce rank3 within a fixed two-vector
quadric subspace before upgrading to Euclidean cameras.

Keep pOSE/projective refinement/Euclidean BA/held scorer/data/losses/seeds/bounds
from7f3eade. Reuse our own code throughapply_patch only after this registration.
No framework/model/weight/download/training/upload or source-scan geometry.

## Fixed finite algebraic candidates and training-only choice

Build exactly the same linear quadric constraints. Always retain the two last
right singular vectors A,B,not a tuned nullity/rank cutoff or a vector sweep.
Enumerate the four homogeneous generalized eigenpairs of(A,-B),representing
singular quadrics beta*A+alpha*B. Include roots at infinity;record every root.
Reject zero/zero pairs(singular pencil),nonreal roots(imaginary relative>1e-7),
nonfinite/zero matrices and matrices without exactly three positive numerical
modes and one null mode(tolerance1e-10times matrix spectral magnitude). Signs
normalize by positive trace;no negative-mode clamp or extra nonlinear optimizer.
These are computational rank/realness criteria,not pixel/mm accuracy claims.

For each remaining rank3quadric use its positive eigenbasis and null vector
to form H. Enumerate the same two last-column signs,perform the same RQ/proper
camera decomposition and medianfx/fy sharedf. A candidate is eligible only if
finite,proper,all observed TRAINING depths positive andf strictly(400,4000).
Record intrinsic mismatch/all candidate rejections. Choose smallest native-pixel
training mean-squared projection error under that sharedK BEFORE held scoring;
ties by generalized eigenpair index then positive sign. No held/known true
focal/pose/3D/medical error selects the candidate. One Euclidean BA after choice,
not one BA per root. All old native-pixel/cheirality/held gates remain unchanged.

First deterministic algebra check:A=diag(1,1,1,0),B=diag(0,0,0,1) must retain
the rank3solution and reject the rank1infinite root(s),also under fixed2/3 basis
scaling. A rank2plusrank1 pencil with a common null vector must fail closed.
No tolerance adjustment after results. Then validate the saved0283control
prefix archiveSHA45636fc9c2d9cb1a534e5ce5f60b0f5865709d5d00ea1377f0fbf497bfd2014f,
read onlycontrol-projective.npz(480training points/five projective cameras).
Replay its trainingp95<=.001nativepx. Do NOT rerun pOSE/projective optimization
or read true control cameras/3D into inference. The completed prefix/gradient
checks are inherited,not a new end-to-end execution. New upgrade+one Euclidean
BA+unchanged480held/negative checks use exactseed280control observations as
before. Require heldp95<.1px,zero invalids,negative17*view_index^2check fails3px.
Report control mode explicitly:FROZEN_PREFIX_NEW_UPGRADE. Failure stops before
patient data;do not relabel0283's original failure as a pass.

If control passes,run the full unchanged pOSE/projective prefix ONCE on authorized
case001's frozen0267 observations,then new upgrade,one Euclidean BA and all whole
held-ID LOO projections. Same74frames0..876,59448rows,3865training/905held IDs,
native pixels,shared input rights/hash and0267archive SHA. Source scan/bone/
case002 never enter inference;missing888..1040 remains missing. Success at most
PARTIAL_SUCCESS tracked geometric consistency,not physical identity/2mm head/
visualACCEPT. No formal head fitting before actual camera/material gates.

Implementation<=600s,control<=120s,each actualpOSE/projectiveBA/EuclideanBA<=180s,
held<=120s,whole2400s. One configuration/worker,no root/seed/alpha/rank/tolerance/
threshold/point/frame/precision rescue. Ordinary pre-estimate IO repairs disclosed.
On failure preserve compact reports/all roots/prefix source hashes/control
evidence/Git recovery;remove exclusive runner/raw output/bytecode,verify original
hashes/consent/0207/shared tests/defaults,local cleanup commit before another
route. No new dependencies,paid/noncommercial asset,push or fake acceptance.
