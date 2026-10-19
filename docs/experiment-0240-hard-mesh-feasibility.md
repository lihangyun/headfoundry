# Experiment0240: hard geometry feasibility, not another identity ridge sweep

Date:2026-10-19. Pre-registered before implementation/solve.
Status:`TECHNICAL_CHECK_PASSED` for bounded facial capacity/local mesh guards;
full-head visual promotion remains`REJECT`, video-only acceptance`UNVERIFIED`.
Role:`SCAN_ORACLE_NOT_VIDEO_RECONSTRUCTION`.

0239 provides new causal evidence: its unchanged300-D anatomical representation
fits all seven face-region proximity targets, but39 body facets violate full
mesh guards around eyelids/ears. Neither eyeball component is damaged. A box on
identity parameters is not a physical mesh constraint. Test one new mechanism:
enforce whole-output geometry feasibility **inside** the identity optimization.
Do not change the prior,regions,regularizer,alignment,feature model or observations.

Freeze0239's final saved `fit-step-04` quadratic H,g (including4mm^2 ridge), mean,
world-space identity basis, coefficient bounds[-3,3], complete original topology
and one global similarity. This is one fixed-correspondence local capacity
diagnostic, not another5-step nearest-point fit and not a globally optimal shape
claim. The unsafe unconstrained result supplies only initial violating face IDs;
start optimization from the safe zero-identity prior, not a scaled final fit.

For each constrained original triangle, require normalized prior-normal dot
>=1e-6, area ratio>=.20001 and<=4.99999. These conservative numerical margins
imply the unchanged final .2..5 area and zero-reversal guard; they do not relax
it. Use analytic derivatives of cross-product normals and test against central
finite differences. No post-fit smoothing,coefficient scaling,masking,topology
deletion or mouth/eye closure edits.

Use existing SciPy SLSQP, exact objective gradient, tolerance1e-9,max200 iterations
per round. Divide objective and gradient by one fixed max(1,max(abs(g))) constant
for numerics only. Begin with all39 failing faces, then inspect **every** original
face after each solve. Add all newly violating IDs and restart from safe zero,
up to5 rounds, one180s total process budget. Stop immediately on optimizer failure,
unchanged violated set or exhausted budget. No best-iterate fallback,parameter
search,alternative solver or relaxed constraint. Constraint generation is output
feasibility, not removal of data or error-based source-region selection.

Before the first solve, fix exact Hessian whitening: with scale s=max(1,max(abs(g)))
and H=L*L.T, set beta=sqrt(s)*inv(L.T)*z. This makes the normalized quadratic
Hessian identity without changing its objective or identity prior; beta bounds
remain explicit linear inequalities. Use inner box margin1e-8 and constraint
arithmetic tolerance1e-7. The declared area/orientation margins still imply the
original strict final mesh guards. Save this invertible numerical transform;
do not choose another conditioning scheme after inspecting results.

Only a successful optimizer with full hard constraints and original mesh guard
may export a reviewable oracle. Keep the entire fixed quadratic and all facet
IDs,iterations,Jacobians/KKT evidence and actual coefficients for replay. Evaluate
the unchanged19336 source samples,5000 whole-output samples, all seven face p95s,
full-source/reverse errors and coverage. Recheck nearest-support first-hit status.
Render source,aligned neutral and safe oracle under exactly0239's common cameras
and lights; no per-mesh normalization.182 prior tests must remain passing.

Success here requires mesh safety **and** all seven region p95<=2mm plus actual
anatomy review. Any failure freezes this hard-feasibility configuration and the
tested linear-prior oracle branch without more penalties,weights,bases or step
scales. A positive result only establishes a bounded scan-fit capacity candidate;
62 native open edges,unscoped full head,closed eyes/source defects,unknown scan
accuracy,video-only camera/inference,case002 and user acceptance remain required.
Never transfer its scan-derived identity into the video-only pipeline. Only
case001 local validation is used; no training/upload or production changes.

## Executed result

The fixed whitened objective converges in12 SLSQP iterations,one round,2.59s.
All9976 original faces pass the hard inequalities within the fixed arithmetic
tolerance and the **original strict** mesh guards:0 prior-relative normal
reversals,min area ratio0.200010,max4.999990. No vertex/face/region is removed,
and no coefficient scaling,smoothing,source refit or new alignment is performed.
Independent local KKT multiplier reconstruction gives stationarity-infinity
residual7.65e-8; this is not proof of global optimality. Objective transformation
replays within7.28e-12 and the complete exported OBJ within5.12e-13mm.

| Source region | Box-only0239 p95 mm | Hard-feasible0240 p95 mm |
| --- | --- | --- |
| Nose | 1.304578 | 1.346975 |
| Perioral | 0.799711 | 0.806370 |
| Chin | 0.525645 | 0.534723 |
| Left image cheek | 0.454303 | 0.463021 |
| Right image cheek | 0.469394 | 0.463394 |
| Forehead | 0.904806 | 0.941402 |
| Other frontal face | 0.568757 | 0.580928 |

All seven coarse facial proximity targets remain below2mm after geometry
constraints. This is a scan-fitted capacity result, not improved video inference.
Full-source p95=22.459mm and whole-output reverse p95=43.079mm still fail the
complete-head target; native62 open edges remain.11/7168 nearest fit supports
remain hidden, so nearest proximity is not accepted material correspondence.

All18 actual common-camera source/neutral/constrained-oracle views are inspected,
including bilateral90degrees,obliques and back. The facial fit moves toward the
source without a gross new eyelid/ear fold in these renders. Generic eyelids,
cranial outline,ear identity,neck/cut domain and posterior source artifacts remain
unmatched/unverified. This limited visual screen is not a self-intersection,
medical anatomy,whole-head likeness or user acceptance certificate. Private
review records explicitly reject full-head promotion and label the scan oracle.

All184 regression tests pass,including finite-difference Jacobians and invariance
under proper similarity/unit changes. The constraints can therefore operate on
the native generic prior without importing a subject's scan alignment. No new
model or dependency is installed; source/defaults/case002 remain unchanged.

Stop this oracle branch here: no further scan-fitting/regularizer/constraint
tuning. Next pre-register a genuinely **scan-free global model-based video**
experiment from zero identity/native prior,with independent observation/camera
checks. Neither these source-derived coefficients,nor their similarity,quadratic
or fitted geometry may initialize it. The skin scan is evaluation-only there.
Full-head/profile/mesh/uncertainty/case002 and actual user visual gates stay intact.
