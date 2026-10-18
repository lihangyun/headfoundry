# Experiment0214: unique normal-line target observations

Pre-registered2026-10-18. The0213 coverage audit locates a large omitted posterior
cranium component away from target boundaries, separate from lower-neck boundary
differences. Hypothesis: surface-directed observations can recover that valid
coverage without pushing mismatched open boundaries into the head.

Change one primary variable: replace trimmed nearest-sample matching with exact
triangle intersections along each current source vertex normal in both signs.
Accept only one distinct crossing within+/-0.12 target-radius units, with target
triangle normal dot source normal>0.25 and hit y below the original neck cutoff.
Merge duplicate triangle-edge hits within2e-8; multiple distinct crossings,
misses, incompatible normals and out-of-scope sources remain unsupported.
No distance-percentile selection. This is a different observation construction,
not a revised percentile, known anatomical mapping or a photograph predictor.

Keep0213's GNM30 prior, geometry, pose, first four FLAME Open targets, source
scope, fourfold unsupported-rest weight,0.05 data strength,10 outer/20 inner
local-rigidity iterations, safe half-steps, full independent metrics, cameras,
rendering and30% gate. Source and target asset chains remain pinned. The same
target surfaces provide both methods' observations; exact triangle intersection
replaces sampled closest-point association. No new model, photo fitting or data.

First run original case00 once. Require all mesh/protected gates and>=30%
symmetric-distance reduction over the original frozen GNM30 baseline. Only then
render five fixed views and inspect posterior/neck form and facial shape. Visible
fold/kink, no useful target-shape recovery or a numeric miss ends the scheme.
Only a passing screen permits the other three original cases; all must be safe
and protected, at least3/4 reach30%, and all need actual five-view review.

Budget15 minutes fitting/evaluation plus15 minutes rendering/review. One run per
case, one correction only for an identified implementation error. No ray-range,
normal-angle, ambiguity, scope, safety, strength or iteration sweeps. No post-fit
shrinking/smoothing. Defaults, subject head, cameras, hair and texture unchanged.
Success would be limited synthetic registration evidence; real-reference likeness
and physical-camera recovery still require their own evidence.

## Results

Case00 completed in100.718s, ten full safe updates with no halvings. Unique
supports range9595–9636; ambiguous crossings range753–778. Symmetric sampled RMS
falls0.04196115→0.01723912 (58.916%). Left/right profile depth RMS falls
0.06427430/0.06178459→0.02750572/0.03000919. Nose/lip/chin and all five depth guards
pass. Actual export minimum area0.566841, zero reversals, maximum displacement
0.102710 radius. Numerical registration: `PARTIAL_SUCCESS`.

Fifteen fixed-camera renders complete in5.542s; maximum projection replay error
0.000116643px. Full five-view and nose-lip-chin sheets show substantially better
posterior cranial extent, confirming the coverage mechanism helps. However a
new curved ridge appears near the lower neck, clearly visible on the right
profile; shoulder/neck margins also change unnaturally. Nose/lip detail remains
different from the target. **Whole-head visual decision: `REJECT`.** The topology
already differs at the eyes and lower cut; those existing differences are not
new successes or automatically blamed on this candidate.

Stop before cases01–03. No ray-range/angle/ambiguity/iteration sweep or smoothing.
The saved candidate stays frozen. Known-target posterior coverage is a useful
limited improvement, not a reference-photo reconstruction or overall acceptance.
Actual sheets and `.blend` are local in `artifacts/experiment-0214/`.

The remaining boundary hypothesis is now separate: unsupported surface vertices
are currently assigned fourfold positional observations at the prior, including
the excluded neck. Such invented fixed positions may conflict with observed
deformation. A missing-observation formulation may be tested independently with
the same normal-line observations and solver, preserving the numerical influence
of actual observations and all safety/visual gates. That must be a single
pre-registered binary objective comparison, not a rest-weight parameter sweep
or a retroactive repair/promotion of0214.
