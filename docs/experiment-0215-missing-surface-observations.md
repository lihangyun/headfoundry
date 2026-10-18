# Experiment0215: missing observations instead of prior-position pseudo-data

Pre-registered2026-10-18 after0214's actual visual rejection. Its posterior
recovery is useful, but a lower-neck ridge remains where supported deformation
meets unsupported vertices pulled toward their prior positions. Hypothesis:
that data model introduces an artificial positional conflict at coverage edges.

One binary objective change: unsupported vertices contribute **zero positional
data**, allowing the same local-rigidity energy to extend the deformation over
them. Observed vertices retain exactly the old data coefficients: use the old
all-vertex weight mean as the normalization denominator, then zero unsupported
weights. Do not renormalize the remaining observations to make them stronger.
Every mesh-connected component must still contain positive observed weight so
the positional solve is anchored. This is an explicit missing-data formulation,
not another positive rest-weight value or a collision/volume guarantee.

Keep0214's exact normal-line range/ambiguity/angle/scope rule, same original
GNM30 prior, FLAME Open targets, data strength0.05,10 outer/20 inner steps,
all safety half-step rules, full evaluation denominator and fixed five views.
No new target, mask, geometry topology, smoothing, model or photo fitting.

Run only case00 first, once. It must pass the same30% symmetric-distance gain,
regional/depth non-regression and mesh gates, then show useful target recovery
without the lower-neck ridge or another visible regression. Failure stops this
objective formulation without trying partial-rest weights or additional terms.
Only an actual numeric and visual pass permits the other three original cases;
all must pass mesh/protected checks, at least3/4 reach30%, and all need visual
review. Full objective remains a recognizable head from the user references;
synthetic registration alone does not complete it.

Budget15 minutes fitting/evaluation and15 minutes rendering/review. One correction
only for a diagnosed implementation defect. All previous outputs remain; no
defaults or subject assets change.

## Results

Case00 completes in98.627s. Symmetric sampled RMS drops0.04196115→0.01155467
(72.463%); forward/reverse RMS is0.00578354/0.01528305. Left/right profile depth
RMS drops to0.02018424/0.02011873. All protected regional/five-view checks pass.
Actual export minimum area0.581673, zero reversals, maximum displacement0.119982
radius. Iterations0–5 accept full steps; iterations6–9 use the predeclared1/2/3/4
halvings as the displacement constraint becomes active. No post-fit shrink.

Fifteen actual fixed-view renders take5.740s with maximum projection replay
0.000116643px. The curved posterior neck ridge is reduced and cranial recovery
remains visible. However the now-free lower-neck margins curl/undulate in front
and oblique views; the neck cut remains unlike the target. Facial differences
also remain. Thus limited numeric registration is `PARTIAL_SUCCESS`, but the
**whole-head visual result is `REJECT`**. Stop before cases01–03, with no
partial-rest weights, extra objective terms, smoothing or relaxed safety.

This narrows the interpretation: valid posterior observations were missing;
the neck also has a source/target boundary correspondence problem which neither
fixed prior positions nor free extension solves. Do not keep spending the next
person-reconstruction experiments on this same cross-model neck setup. The
original four-case registration benchmark remains unpassed; a single synthetic
mean head is not evidence of real-reference likeness or general registration.

Implementation uses the existing runner with explicit observation/policy
arguments; the original0213 default behavior remains positive-weight fitting.
The shared solver now permits zero weights only when each connected component
has a positive positional anchor. Two meaningful checks verify rigid motion
propagation with missing data and rejection of an unanchored disconnected
component. Together with ray intersection checks, all132 public tests pass.
No added dependency, asset, training, photo processing or default change.

Exact meshes, arrays, input/code hashes,15 renders and `.blend` are local in
`artifacts/experiment-0215/`. The0214 runner/helper source snapshots are preserved
under its own artifact folder and independently match its recorded execution
hashes; source evolution does not overwrite previous evidence.

```text
.venv/Scripts/python.exe tools/experiment_0215.py
blender --background --python tools/render_capacity_0208.py -- artifacts/experiment-0215
.venv/Scripts/python.exe tools/review_capacity_0208.py artifacts/experiment-0215
.venv/Scripts/python.exe -m unittest discover -s tests
```

Runners refuse overwrites. The actual failed outputs are retained. Full-view
inspection must accompany any facial crop so neck defects are not hidden.
