# Audit0338:cycle closure is not physical endpoint precision

Registered2026-10-23T03:54:00Z,after independent0337cleanup e78c0e6 and BEFORE
new controls. Budget1200s through report/tests/local commit,deadline04:14:00Z.
No reconstruction candidate,model runtime,clinical data rescore or camera fit.

## Question and bounded method

0337stopped at7/96complete FB<=.75px tracks versus registered48. Its true endpoint,
camera and medical errors were never measured. Test whether that policy is a
necessary or sufficient mathematical condition for physical pixel accuracy.
This differs from0286's along-epipolar ambiguity and0300's coordinate-free graph
cliques:here the object is the actual numeric forward/backward pixel composition.
Do not rescue0337,lower48,raise.75,restore weights or choose a new threshold from
its saved errors. Its REJECTentry and unmeasured geometry remain unchanged.

Use only existing NumPy and shared native bilinear sampler. Fixed128x96image,
96source queries on12x8grid x24..64,y24..56. True invertible affine map
F(q)=diag(1.25,.8)q+[8,12],inverseB. All sampled endpoints must remain within
the complete interpolation domain;no occlusion/bounds trick or point pruning.
One primary variable is the relationship between independently specified true
endpoint errors and the measured cycle,not scene/threshold/model variation.

Fixed analytical controls,not a sweep:
1. Exact true forward/inverse maps:zero physical error and zero cycle.
2. Add[1,0]px to BOTH maps:both endpoint errors1px<3,but cycle1.8px>.75.
3. Add[16,0]px forward and[-12.8,0]px backward:physical errors16/12.8px>3,
   but cyclezero. Derived inverse-bias cancellation,not a learned field.
4. Independent rectified pinhole arithmetic f1200px,baseline100mm,Z1000mm:
   true disparity120px;fixed2px disparity underestimation predicts120000/118mm.
   This is point-depth sensitivity only,not actual medical surface accuracy.

Derive the general bound under visible invertibleB with local LipschitzL:
cycle<=L*forward_error+backward_error_at_predicted_endpoint. No converse without
independent error bounds. Check the controls with float64 roundoff only(1e-10px,
well below the physical thresholds),using ALL96queries. No estimator tuning.
Two target masks each with48admitted disjoint IDs also demonstrate that marginal
counts alone cannot imply any joint support;this is counting,not a data selector.

## Scope,stop and verification

Keep only small generic regression tests and this report;no exclusive model,
framework,clinical script or generated head to accumulate. One bounded test run
<=120s/1GiB through existing process-tree monitor,then complete shared suite
<=120s/1GiB. Any failed analytical identity stops the audit;ordinary unscored
test/code errors may be documented,not used to alter the fixed witnesses.
No human/scan/case002 input is read,uploaded or trained on;0207/defaults untouched.

TECHNICAL_CHECK_PASSED would certify these counterexamples and the logical scope
only,not that0337's rejected predictions are accurate. It cannot certify any
camera or justify an automatic replacement admission rule. Actual3pxcamera,
fixed skin-surfacep95<=2mm,mesh/full-head and user visual gates stay intact.
Future observation admission needs a separately registered validation of the
actual estimator/noise/support/information and independent held evidence;the
audit must not turn into replaying retired observations under relaxed filters.

## Result:TECHNICAL_CHECK_PASSED logical audit,real reconstruction UNVERIFIED

All fixed controls pass on the first run. Native bilinear composition reports:

| Fixed error construction | Forward EPEp95 px | Backward EPEp95 px | Cyclep95 px | FB.75admits |
|---|---:|---:|---:|---:|
| Exact fields | 7.11e-15 | 7.11e-15 | 1.59e-14 | 96/96 |
| Independent+1pxbiases | 1 | 1 | 1.8000000000000114 | 0/96 |
| Cancelling wrong biases | 16 | 12.8 | 1.59e-14 | 96/96 |

All96queries/endpoints have complete native support,no error pruning. Roundoff
tolerance1e-10only checks the predefined algebra;FB.75andphysical3pxare unchanged.
Disjoint48/96pairwise masks yield0joint support. This demonstrates no implication
from marginal counts,not a probability model for0337's observed7joint tracks.
The independent depth arithmetic returns16.9491525424mm error for2px disparity
error. It is a fixed stereo point-depth counterexample,NOTthe skin-surface metric
or an estimate of actual video baseline,focal,depth or error.

Let eF=Fhat(q)-F(q),eB(v)=Bhat(v)-B(v),v=Fhat(q). With exact visible inverseB,
  Bhat(v)-q = [B(F(q)+eF)-B(F(q))]+eB(v).
Triangle inequality and a Lipschitz bound on the relevant segment give
  ||cycle|| <= L*||eF||+||eB(v)||.
For this affine inverse,L=1.25. Low endpoint error therefore does not imply
cycle<=.75;neither does a zero cycle bound either physical error without extra
independent information. Occlusion/noninvertibility can weaken the assumptions
further,but neither is needed for these counterexamples. This is not a measured
skin-noise distribution,sensitivity/specificity study or new optimal threshold.

The0333ledger's earlier word"necessary"for numericFBdiagnostics was too strong
as a claim about physical accuracy;correct its wording with this explicit audit.
Keep every historical registered decision and its original gates unchanged.
Conservative internal admission may legitimately stop a prototype;that stop is
an operationalREJECT,not proof of true endpoint/camera/medical precision failure.
In particular,0337could be physically wrong OR could contain useful predictions;
this audit does not determine which. No retired candidate is promoted/restored.

No replacement selector is implemented. Before a different actual reconstruction
attempt,prospectively validate its observation/noise/support and identifiable
training graph against independent physical truth and untouched held evidence.
Do not substitute closure,epipolar error or convergence for physical accuracy,
and do not use the present audit to bypass poor real observations or fit a head.

## Verification and retained scope

Four oracle tests pass0.250s,bounded process-tree0.813s/56823808bytes. Complete
shared suite160tests passes9.516s,bounded11.484s/503693312bytes. No failed test/
second scientific run. Private cycle-logic-0338keeps tiny logs,terminal worker
receipts,source hashes and0207identity
eebdad1f8c22de9773927ae1e8961ed3159077f84ffff9b14298c0a3290ae8ef.
Generic regression extends tests/test_endpoint_oracle.py;no new shared framework
or dependency. One local orchestration helper only schedules existing unittest/
budget monitor;it is not a clinical/model integration. All study inputs,defaults,
previous0337archive and itsREJECTare untouched. No new patient pixels/model/scan
read,training,upload,generated mesh,medical score or userACCEPT. No failed route
bulk exists to clean. Goal remains active;commit occurs within04:14:00Zbudget.
