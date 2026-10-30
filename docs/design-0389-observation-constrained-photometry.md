# 0389: admission design for observation-constrained photometry

2026-10-29. Design only; no new solve, image extraction or model run. Latest
evidence0388(47e100c) shows photometric-only depth drift, not merely slow
convergence. Short account window95%used at entry; checkpoint design before
starting a separately budgeted implementation. This is NOT a reported success
or a replay authorization for any old weights.

## Material change and falsifiable claim

Keep the same raw-image objective but explicitly preserve image-observation
consistency in its feasible set. Unlike0387, moving a training projection50px
away from its supplied coordinate must be infeasible even if intensity matches.
This changes the missing information constraint, not a sweep of photometric
weights, old depthbounds, frames or iteration limits.

Candidate formulation: minimize original sampled photometric loss subject to
each target training observation's Euclidean reprojection discrepancy<=3nativepx,
proper/positive finite camera domain and existing scalar bounds. Source rays
remain fixed.3px is the existing operational pixel gate, NOT an inferred noise
standard deviation or claim that all input correspondences are physicallytrue.
Keep all28training points; no residual-based removal. The original9held points
never enter constraints, loss, step selection or feasibility restoration.

The real0385/0387states have already been examined; future scores on this split
are development evidence, not a fresh independent estimate of generalization.
The candidate may improve constraints while worsening true geometry. It must
not inheritACCEPT from feasibility or low photometric cost.

## Required implementation checks before patient execution

1. Implement the minimum constraint evaluator in existing NumPy/camera math.
   At a fixed known three-camera/point fixture, exact coordinates are feasible;
   a50px mismatch must fail regardless of the photometric objective value.
2. Biased-observation counterexample: shift a supplied coordinate by6px while
   keeping physical geometry fixed. The true geometry must become infeasible
   for that row; a geometry chosen to fit biased inputs must NOT be called true
   solely because constraints pass. This exposes the method's assumption,
   not a reason to drop that row or relax3px.
3. Validate numerical constraint derivatives against independent differences,
   reject nonfinite/negative depth before optimizer use, and verify fixed
   held-coordinate bytes never reach objective/constraint construction.
4. Candidate optimizer must report feasibility and convergence separately.
   A numerical termination with violated constraints isREJECT, notPARTIAL_SUCCESS.
   A constrained optimizer is an implementation necessity, not evidence of
   superiority overTRF. No arbitrary weighted geometric+photometric sum.

Only after checks, separately freeze the optimizer configuration/time/memory,
input hashes and termination criteria before running one actual attempt.
Start from archived0385original state, not the drifted0387final state. Check
starting per-observation feasibility explicitly; if it fails, stop rather than
silently project, prune or switch starts. Do not infer feasibility fromp95alone.
One candidate, no weight/constraint/solver/seed search. Final original9held
three-view predictive3px check remains required, plus all physical/fullhead
medical2mm/useracceptance gates; no headfit on synthetic checks alone.

## Stop/retention policy

If controls contradict the constraint contract, fix ordinary implementation
errors before any patient solve and retain the failed check. If the scientifically
fixed real trial fails, preserve compact reports/hashes/recovery and clean its
exclusive source/output before any new route. Keep shared originals/fixtures,
case002untouched and no patient training/upload. No changed production defaults.
This document does not claim the complete head target is attainable under the
present inputs or that constraints alone add new physical information.

## 2026-10-30 implementation admission

Added minimal purethree-view constraint evaluator with analytic chain through
fixed source rays, logf and log inverse depth. No assets/solver/ACCEPT inference.
Three tests pass: exact,3pxboundary,6pxbiased and50pxmismatch; allparameter
central differences; negative/nonfinite depth and malformed arrays. Maximum
normalized derivative discrepancy5.87825e-7. Exposure columns correctlyzero.
Bias control demonstrates that true geometry may be infeasible if observations
are wrong; this component is not an estimator of physical correspondence truth.

Read-only0387archive check, original training indices only: original ray-start
maximum discrepancy1.712715px, all56targetobservations feasible, minimum
slack6.066607px_squared. Rejected0387final violates47/56constraints, maximum
discrepancy75.583617px. This verifies that the proposed constraint would detect
the observed drift without silently repairing the start. Neither state refit.
