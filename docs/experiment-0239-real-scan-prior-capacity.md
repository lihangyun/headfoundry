# Experiment0239: anatomical identity-prior capacity on independent real skin

Date:2026-10-19. Pre-registered before source/prior preview, registration or fit.
Status:`REJECT` despite low facial proximity errors.
Role:`SCAN_ORACLE_NOT_VIDEO_RECONSTRUCTION`.

Automatic local measurements0235/38 and direct geometry0236 have failed their
precision gates. Before a distinct global anatomical-model image fit, ask if
the existing legally cleared complete-head representation can express this
real face.0143's rejected AI-reference/0132-transfer fits did not use an
independent real skin scan; the newly authorized source supplies different
shape evidence, not permission to sweep the old reference configuration.

Use only the exact locked CC-BY-4.0 FLAME2023 Open safe300-dimensional identity
asset and case001 source/0237 reviewed triangle-region samples. No GNM patches,
free vertex displacement, added expression model, source topology edit or new
asset. No video pixels or video cameras are fit. Source eyes/cuts and unknown
acquisition/semantic uncertainty remain explicit; case002 stays reserved.

Stage1:read-only model readiness. Verify every original/converted asset hash and
render the native neutral prior with +Y-up,+Z-front cameras before registration.
Inspect front/bilateral45/bilateral90/back. Do not inherit0143's project-coordinate
sign conversion without checking native anatomy. Confirm finite unit basis,
proper axes and unaltered prior topology; record its open boundaries rather than
calling it a watertight accepted head. Stop if this prerequisite fails.

Stage2:one mean alignment, then one bounded identity fit. Initialize1000 model
units-to-mm and translate the template's maximal+Z vertex (nasal tip in reviewed
native orientation) to the source's maximal+Z vertex. Fit **one whole-head proper
similarity**,10 closest-triangle iterations on even-indexed samples in each of
the seven frozen face groups (7168 total), with group area weights normalized to
mean1. No distance trimming or region removal. Reject uniform scale outside
700..1300mm/model-unit or rotation>15degrees from identity. Freeze this similarity
before any identity fit and apply it to every vertex/region for both variants.

Primary variable is the300-D anatomical identity vector, not pose/alignment.
Five closest-triangle iterations use exact Blender BVH queries and barycentric
interpolation of the **unchanged** template/basis. Solve each finite positive
quadratic with coefficient bounds[-3,3], L2 weight4mm^2 (a fixed engineering
prior, not a claimed scanner-noise estimate); no bound clipping after an
unconstrained solve. Use a tested box-QP solver with at most2000 iterations,
relative projected-KKT<=1e-6; failure stops, no solver/regularizer sweep.

Protect original full topology and finite shape. Require min triangle area ratio
>=.2,max<=5 and no normal reversals over the entire head before any oracle
white-mesh review. Preserve an unsafe result as rejected, without smoothing,
coefficient rescaling or post-fit capping. Count original boundary/nonmanifold
edges separately. This is not a closed-mouth, eyelid or anatomical certificate.

Evaluate baseline/oracle against **all**19336 fixed source samples and5000
area-uniform whole-output samples with the existing exact distance helpers and
same frozen alignment. Report all seven region p95s, full-source p95, full reverse
error/coverage, and the odd-index region samples separately (quadrature checks,
not independent people/capture evidence). Report first-hit visibility of final
nearest fit supports; hidden proximity must not be described as material
correspondence or used to certify anatomy. Regional numeric capacity requires
all seven source-region p95<=2mm and mesh guards. Full-source/full-head acceptance
remains separate and unproven even if that narrower capacity check passes.

Render actual source, aligned neutral prior and safe oracle under common front,
both45,both90 and back cameras/lights; visibly label the oracle scan-derived,
not video-derived. Inspect nose/lips/chin, aperture and ear/neck/posterior changes.
Do not claim likeness improvement from nearest-surface distance or a self-fit.

One180s fitting process and at most60s additional rendering, no parameter/model/
region/similarity/shape-basis sweep. A failed face capacity or actual anatomy
review freezes this tested linear identity route. A positive diagnostic only
permits a separately predeclared **scan-free global image-fitting** experiment;
it does not waive real camera/observation, full-head, uncertainty, case002 or
user visual gates. Originals, failed results and production defaults stay
unchanged. No training/upload, source-as-output substitution or private services.

## Numerical implementation audit, before one repaired replay

The first run stops at its **first** identity quadratic, before any identity
candidate or capacity result. The fixed positive-definite Hessian has condition
28237.1;2000 first-order FISTA steps leave projected-KKT4.6263e-5, above1e-6.
This is an uncompleted numerical solve, not evidence of prior incapacity.
Preserve the exact Hessian,linear term,initial fit inputs, failed process and
producer. Do not increase iteration/runtime limits, change the prior or reinterpret
the nonconverged iterate as a valid fit.

Authorize one implementation-only replacement: a deterministic primal active-set
box-QP solve using exact free-subspace linear solves and feasibility line steps.
Keep the same objective, bounds, KKT threshold,2000-iteration ceiling and all
anatomical/metric gates. Before a new head fit, independently compare its solution
against installed SciPy BVLS on the **unchanged saved first quadratic**. Require
max coefficient difference<=1e-5 and original-Hessian projected-KKT<=1e-6.
Also test a manufactured correlated active-bound problem and a poorly conditioned
interior optimum. The replay must assert its first objective/data are bit-identical
to the saved failure. Use a separate output; no further numerical-solver or
regularizer search if this one repaired replay fails. This repairs the specified
bounded solve, not a post-hoc search for better scan-error numbers.

## Result: useful facial capacity, unsafe whole output

The one repaired replay completes fitting/evaluation in27.27s. It verifies the
first objective,closest faces,barycentric data,targets and weights bit-identical
to the stopped run. Independent SciPy BVLS agrees with all five saved box-QP
solutions within2.15e-13 in coefficient value. Identity and complete OBJ replay
errors are<=5.12e-13mm; original5023 vertices,9976 faces and topology remain.
All182 regression tests pass. No original/default/case002 or source region changes.

| Frozen source region | Aligned neutral p95 mm | Scan-fit oracle p95 mm |
| --- | --- | --- |
| Nose | 5.209930 | 1.304578 |
| Perioral | 2.551907 | 0.799711 |
| Chin | 4.772823 | 0.525645 |
| Left image cheek | 5.086356 | 0.454303 |
| Right image cheek | 4.854572 | 0.469394 |
| Forehead | 4.332044 | 0.904806 |
| Other frontal face | 5.336381 | 0.568757 |

All seven facial numeric proximity targets pass, including similar odd-sample
quadrature errors, but **the complete diagnostic is REJECT**. Whole-head guards
find31 prior-relative normal reversals,min area ratio0.027959,max14.434008.
There are39 unique failing facets, including6 undersized and5 oversized ones.
All are on the3931-vertex body; neither546-vertex eyeball component is damaged.
Read-only nearest-source labeling puts33 outside the coarse face scope and6
near its forehead label, at distances0.037-16.680mm. Those labels are not precise
anatomy: actual first-hit-visible markers on the unchanged safe neutral prior
localize problems around eyelid/ear regions. Do not trim these facets or expand
the eye exclusion to manufacture safety.13/7168 final closest fitting supports
also lack first-hit support; proximity is not proven material correspondence.

The full-source p95 is22.397mm and whole-output reverse p95 is43.817mm, including
unscoped scalp/neck/domain differences. The prior also retains62 open boundary
edges. None of this is complete-head, physical scan accuracy or likeness
acceptance. Actual source/aligned-neutral common-camera views were inspected;
the unsafe oracle was deliberately **not rendered** as a result. A six-view
safe-prior marker audit is a failure-location diagram, not the fitted geometry.

Stop this unconstrained-in-mesh identity configuration. No regularizer,basis,
coefficient-amplitude or mask rescue follows. A separately predeclared single
**hard mesh-feasibility** experiment is justified by this newly localized damage:
keep this exact data objective/pose/basis and constrain output geometry itself
during optimization, testing all facets again before rendering. If that fails,
freeze this route without successive safety-penalty or scale sweeps. Even a
safe scan-fit remains an oracle; its identity coefficients may not seed or
masquerade as the required scan-free video inference.
