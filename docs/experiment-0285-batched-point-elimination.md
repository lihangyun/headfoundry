# Experiment0285: fixed-input point-elimination equality and timing first

Registered2026-10-21T13:05:42Z,before audit/optimization. Whole2400s includes
implementation,audit,one control,at most one actual cohort,evidence/cleanup/tests.
0284 is closed/cleaned atc064002;goal/head/medical/visual acceptance unchanged.

Evidence:0284's actual pOSE prefix times out at180s without a completed model;
its scalar evaluator loops over3865points,solving a small SVD least-squares
problem per point per evaluation. That is a plausible cost,not an established
sole bottleneck. Main engineering variable:one batched SVD evaluation of these
same conditional point systems and vectorized objective/gradient accumulation.
No scientific objective,alpha/seed,iteration/phase budgets,precision,camera/
point/frame/holdout/rank cutoff,quadric branch rule or physical gate is changed.

## Prospective audit,not an optimizer replay

Use only authorizedcase001video manifest/hash and exact0267observations archive
SHA54aa2b303e4fa6f0599628f677bf359e4125dccd1df867ea70f8b9e19154c612.
Same74frames0..876,59448rows,3865training/905whole held IDs;held IDs not used
in equality/timing. No scan,bone,case002,upload/training/new runtime/model.
Reuse own d674f42 source throughapply_patch after registration;no failed
framework reinstated. Existing NumPy/SciPy float64,CPU4threads only.

Evaluate exactly three TRAINING-only camera states:originalseed283initial
cameras and plus/minus one deterministicseed285normal perturbation sigma.001
on free camera entries(camera0 unchanged). These are equality probes,not
candidate optimization starts or a search;they cannot select a science result.
For each state once,time the complete original scalar cost/gradient/point
evaluation,then the batched equivalent on the same arrays. Preserve the
reference per-point loop verbatim;only expose its already computed points.
Report all timings,not best-of repetitions. No warmup/timing/point-size sweep.

Batch by zero-padding missing view rows,using reduced SVD of each4Vx3matrix.
Match original per-point lstsq singular cutoff eps*max(4*observed_views,3),
not padded row count;require unchanged full rank3. No normal equations,
downcasting,subsampling,ridge or conditional fallback to a different solver.
Require objective relative difference<=1e-8,gradient infinity-norm relative
difference<=1e-8(denominator max(1,norminf)),and ALL observed native projection
deltas<=.001px. Count nonfinite/zero denominators as failure,not exclusions.
The pixel budget is1/3000of3px,an implementation-difference bound only,not
accuracy against actual material truth. Record point deltas without calling
them metric millimeters. No bitwise optimizer-trajectory equivalence is claimed.
Require scalar/batch median timing speedup>=2 across the three states. Failure
stops before ANY optimization;no batch-size/cutoff/tolerance/precision rescue.

## Only if audit passes:unchanged bounded reconstruction attempt

First rerun ONE full seed280synthetic chain,now including batched pOSE from
scratch(originalseed283generic camera start),projective refinement,rank-three
quadric selection,one Euclidean BA,and untouched480held/negative checks.
This is a fresh full-prefix control,not0284's frozen-prefix mode. Never use
true camera/focal/3D/held/medical data to initialize or choose candidates.
Same heldp95<.1px,zero invalids,negative17*view_index^2xoffset fails3px.
If control passes,one actual cohort uses precisely the same full inputs and
settings as0284,with only batched conditional evaluation and evaluation-count/
last-cost progress instrumentation. Keep pOSE400iterations/1000calls/180s,
projectiveBA60/180s,EuclideanBA60/180s,all gates/bounds unchanged. No replay
after any scientific/resource failure. Intermediate optimizer progress is saved
to distinguish resource use from unmeasured quality;it cannot change stopping.

Actual acceptance still requires proper/positive/focal-valid cameras,training
p95<=3px,all whole held-ID LOO observations,no invalid/weak rays,>=30rows/view,
global AND every-viewheldp95<=3px. Even a pass is at mostPARTIAL_SUCCESS on
unverified tracked identities,not a2mm skin/head or visualACCEPT. No blind
formal head fit,missing888..1040coverage remains unresolved.

Implementation<=600s,equality/timing<=120s,control<=600s,actual eachphase<=180s,
held<=120s,whole2400s. No new dependencies,process duplicates,paid/NC assets,
uploads/training,production/default changes or push. Failed exclusive runners/
outputs/bytecode are archived minimally with hashes/Git recovery then removed;
protect originals/rights/successful fixtures/0207/shared tests,local cleanup
commit before another route. Retain a generic batch-math regression only if
equality genuinely passes,not failed application code or a performance claim
misrepresented as reconstruction improvement.
