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
