# Experiment0245: detector-free profile pose and shared head correction

Date:2026-10-19. Pre-registered before new pose fitting. Status:UNVERIFIED.

0244 stops because the locked detector sees no face in both fitting profiles.
Replace that initialization mechanism with actual visible profile registration,
not another detector/model/crop or a fabricated face. Reuse0244's checked
envelope/pose/frontal-protection math and the complete0243 measured profiles.
All input rights,scan-free baseline,original topology/300 identity bounds,
frontal2px protection,hard native mesh guards,frozen focal/old cameras,separate
scan evaluation and complete-head limitations from0244 remain unchanged.

Exact fitting profiles139/416;development shape-held views69/347 use the same
gradient-ridge settings/ROIs and mandatory image/uncertainty review. Hold each
row indexmod5==0 from both pose and shape fitting. Held views were previously
seen;their **camera poses** now use only their training contour rows on the
fixed baseline head,then freeze before head fitting. Thus final held-view errors
are conditional shape/generalization evidence,not independent camera proof.

No learned detector or old semantic residual enters this branch. Initialize
each proper side camera from native anatomical axes:direction+1→yaw-90deg,
direction-1→yaw+90deg,+Y-up/+Z-front. Use the video's0241 frontal832 depth as
a coarse distance prior and its frozen intrinsic/focal. TranslateXY so the
baseline skin vertex with maximum nativeZ projects onto the observed curve's
anterior extremum. This is a coarse initializer,not a claimed fixed anatomical
correspondence or calibrated camera. Do not use a scan or search nearby frames.

With baseline geometry fixed,estimate each6-D pose once using training row
envelopes/2px and unit Gaussianq prior. Use0244 pose coordinates(.03rad,.005
nativeXY,.03logdepth perq),boundsq[-12,12],SLSQP exact Jacobians,maxiter100,
ftol1e-8. No restart/grid/focal/amplitude/regularizer search. Inspect all four
true-envelope overlays and held-source traces before a head fit. Wrong region,
missing/uncovered rows,nonconvergence or invalid source precision stop this
configuration. All failures and conditional held errors remain recorded.

Then one shared-head correction as0244:beta around the video baseline with
unit Gaussian change,box[-3,3],two fitting-view pose increments bounded[-3,3],
unit pose prior,profile residuals/2px,held rows/views excluded. Hard frontal
all420 model-self anchors within2px,not semantic photo truth. Initial active
mesh faces are selected from this video baseline's own near-boundary guards;
at most5 candidate-driven constraint rounds,restart baseline each round,
SLSQP maxiter120/ftol1e-8. All source profiles/rows remain unchanged. Final
original triangles must pass area/normal guards and exact first-hit support
visibility. Safe failures may only export experimental NOT-ACCEPTED geometry.

Budgets:60s pose preparation,180s single head fit,60s rendering. Separate fixed
scan evaluation must reuse0241's same4x4 and0237's regions/samples,without any
new alignment,ICP,trim or inference feedback. Compare source/baseline/new head
on the same cameras/light/scale. Hold case002 and production defaults. Passing
profile fitting does not prove actual3D improvement,complete topology,physical
camera accuracy,whole-head silhouette IoU or likeness acceptance. Posterior/cap
and source uncertainty remain unverified,not silently waived.

## Pre-fit numerical-domain implementation repair

The original pose139 converges in27 iterations,all213 exact first-hit supports,
held-row p95=5.341px(not accepted camera evidence). During416 optimization a
line-search trial leaves the required row-coverage domain; the low-level exact
envelope raises before a valid next pose can be accepted. Preserve the original
nonzero exit,source capsule and completed139 pose. No shape fit/scan evaluation
has occurred. This is solver-domain handling,not evidence that a source row may
be discarded. Represent invalid trial costs as+infinity,so SLSQP backtracks to
the unchanged finite-domain objective. Accepted states still require every row
and analytic derivatives; no surrogate residual or clipping within the domain.

One declared repair replay writes a new `...0245-domain-replay` output; original
files stay untouched. Replay139's completed pose/initializer to<=1e-8 before
continuing416. A deterministic independent SLSQP fixture verifies+inf trials
backtrack and recover the original valid objective's minimum. Keep identical
frames,curves,parameters,bounds,loss and budgets;record all invalid trial vectors.
If the repaired configuration still fails,do not keep repairing/tuning it.

## Actual stop after the one numerical repair

139 replays exactly(no invalid trials).416 converges16 iterations with2 invalid
line-search trials rejected,213/213 first-hit visible supports and held-row
p95=6.416px.69 converges30 iterations,213/213 visible supports,p95=5.385px.
These are conditional fixed-head pose results,not camera acceptance. The
original139 held p95=5.341px also remains above3px.

347 then fails the predeclared **source measurement** gate:p95 scale uncertainty
3.525px,max26.194px,11/213 rows shift>4px. All213 rows/alternatives remain
preserved;no trace/ROI/parameter/nearby-frame substitution. The repaired full
configuration stops before head fitting and scan evaluation. Overall `REJECT`;
there is no new corrected head from0245. Native pose results,all invalid trial
vectors,original failure/source capsule and uncertain held347 overlay persist
under the original and`-domain-replay` private roots.

This does not erase the two separately reviewed fitting profiles. A subsequent
explicit **unaccepted geometry diagnostic** may test those valid observations
against independent3D scan evidence under the existing user-authorized lane,
but must carry347's failed validation forward and cannot claim the four-view
gate passed. Do not restart0245 or loosen its source/acceptance thresholds.
