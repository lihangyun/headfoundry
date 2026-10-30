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

## Actual outcome: constraint works, optimizer not converged

Registratione7d490d; implementation199c5cc. Intake7.094s/200945664B; exact
originalvideo/1041RGB identities verified through unchanged intake. One fit
worker46.094s/146403328B. SLSQP reached150iterations,7116objective evaluations,
message"Iteration limit reached", optimizer_successfalse. No retry or extension.

Final training constraintmax3.000000019660478px, minimumslack-1.179629e-7
px_squared,0violations beyond predeclared1e-6squared tolerance. This is numerical
constraint satisfaction, not exactly zero floating error or physical accuracy.
Compared with0387tens-of-pixels drift, the new constraint prevents that particular
failure mode on all56targettraining rows. Original observations unchanged.
PhotoRMS0.109468892 ->0.051141289; finalsoftL1cost0.135523875.
Focal1199.776568 ->893.861902px, inside bounds. This is a large estimate change,
not independently measured focal error (true focal remains unknown).

REJECT at nonconvergence, before held evaluation by the registered sequence.
Held3px,medical2mm,fullhead/mesh/useracceptanceUNVERIFIED, not scored failures.
Do not claim finalcandidate has passed camera quality because trainingslack is
feasible. The data-consistency ball allows substantial focal variation, so it
is insufficient by itself to certify calibration. No fixed-state intermediate
candidate was selected, no failed point removed and no original gate changed.
Iteration cap is the direct stopping condition, not a proven unique underlying
cause; this does not establish that additional iterations would solve geometry.

Retain0389pureanalytic constraint evaluator and its negative/bias/derivative
tests: its software contract is independently verified. Do not retain the
nonconverged0390application as a production reconstruction path. No formalhead
or newmedicalerror exists. Future changes require evidence beyond "run longer".

Private archive closed-experiments/0390-constrained-photo/evidence.zip,
378870bytes,19members,SHA53be0c19fbfe1e47ed883925858d165a2cdc3328f95941f9fda51739e9dff710.
Complete start/finalstates, observations, constraints, controlmetadata, logs,
hashes, oneinputsheet and recovery source preserved. Nativegraycopies excluded;
regeneration requires originalvideo decode. No weights/frameworkenvironment.
ArchiveCRC/allmemberhash and11protectedfilehash checks passed before cleanup.

Verified closure:source recoveryc26caee. Allworkers terminal, exact resolved
target/reparse/inventory checks preceded deletion of21loosefiles1240716logical
bytes and oneexclusive runner. Shared0389constraint/tests remain. Aftercleanup
all11protectedhashes,19archive members/CRC/SHA and0383/0385/0387archives match;
no livecaller.170shared tests passed8.829s.0207untouched. Closed00:33UTC within
00:47:46deadline. No complete/ACCEPT claim; fullgoal remains active.
