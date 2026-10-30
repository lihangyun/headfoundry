# 0390: fixed observation-constrained real photometry

2026-10-30 registration00:27:46UTC, whole deadline00:47:46UTC.0389pureconstraint
checks passed,b311381;170shared tests8.910s.0387failed transfer already cleaned.
No new model, download, medicalinput, case002, training or productiondefault.

Single scientific change: preserve all56target training correspondences through
the explicit3px ball constraints while minimizing the same0332photometric loss.
Unlike0387purephotometric objective, depth drift is not free. Constraint threshold
is an operational consistency boundary, not asserted measurement uncertainty.
Input remains0385original seed and exact28train/9held, not0387driftedfinal.
0390is development evidence on a repeatedly inspected split, not unbiased final
generalization. All0385/0387historical results remain unchanged.

Reuse exact0387intake from archived source: verify0383/0385hashes, originalvideo/
consent and1041RGB hashes, frames240/300/630nativePillowL. No extra matching.
Reuse0332source rays,8offsets, pose/depth/exposurebounds; same variable layout.
No initial geometricBA or NN call. Require every starting constraint nonnegative
(0389measured max1.712715px). If not feasible stop, no starting-state repair.

One SLSQP solve (existing SciPy),maxiter150,ftol1e-9, two-point objectivegradient,
analytic constraintgradient from0389. Scalar photometric loss is sum
0.01^2*(sqrt(1+(residual/.01)^2)-1), exactly the priorsoftL1least-squarescost.
No weighted geometricterm. Invalid trial sensor/support/depth domain aborts this
attempt rather than deleting samples. Keep original scalar bounds. Final report
must separate optimizer success, finitepositive domains and constraintfeasibility;
slack tolerance1e-6px_squared accounts for numericaloptimizeraccuracy only, not
a relaxation of the independent held3pxgate. Record actual violations/errors.

One intakeworker<=120s/2GiB, one fitworker<=300s/2GiB, fourmaththreads. No retry,
alternative solver, weights, frame, point, threshold, bounds or iteration sweep.
Allheldcoordinates excluded fromobjective/constraints; check disjoint partition
and preserve observation filebytes before/after. Reading them only for postsolve
evaluation is allowed. Photometricimagecontext is correlated withheldimages;
do not call the9points an independent subject test. Preserve allfinalstates.

After convergence/feasibility only, unchanged0385triangulate-two/predict-third
score on all9held, allviewp95<=3px, propermatrices, positive depths, nonboundf,
wrongcamera+.1raddisplacement>3px. At mostPARTIAL_SUCCESS. Actualmedical2mm,
bilateral/fullhead, earneck/mesh anduseracceptance remainUNVERIFIED. No headfit.
On failure record source/hash/evidence and cleanup exclusive runner/graycopies/
outputs, preserving shared0389tested arithmetic and priorassets. Verify shared
tests and separatecleanupcommit before another route. Wholegoalunfinished.
