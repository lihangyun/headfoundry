# Experiment 0003 — bounded side-profile contour fitting

Status: `TECHNICAL_CHECK_PASSED` on a deterministic contour fixture. Real-photo side-profile improvement remains `UNVERIFIED`.

## Visual target

Move the generic side silhouette toward the observed chin, jaw, and front-neck transition without changing the forehead, nose, lips, crown, occiput, or back neck.

## Hypothesis and counter-evidence

Hypothesis: a small editable contour region with smoothness regularization can materially improve chin/jaw/neck fit without deforming the face core. Counter-evidence: the synthetic target provides exact point correspondence and does not contain camera, segmentation, hair, or landmark noise, so success does not establish real reconstruction quality.

## One primary variable

Enable the side-profile contour constraint. Baseline is the unchanged generic contour; candidate applies a regularized least-squares displacement only to `labiomental`, `pogonion`, `menton`, and `neck_front`.

## Prediction and falsification

Prediction: editable-contour mean error improves by at least 50%, candidate mean error is at most 0.03 normalized units, and protected drift remains zero. Any missed threshold is `REJECT`.

## Protected properties

Forehead, brow, nose bridge/tip, subnasale, lips, crown, back head, occiput, and back neck must not move. Topology and point ordering must remain unchanged. Texture and normals are outside this experiment.

## Commands and results

Baseline fixture: `examples/profile_fixture.json`.

Candidate command:

`C:\Python313\python.exe -m headfoundry.profile examples\profile_fixture.json --svg docs\experiment-0003-profile.svg`

Result on 2026-09-04:

- Baseline editable mean error: 0.0468800.
- Candidate editable mean error: 0.0130090.
- Relative improvement: 72.25%.
- Candidate p95 error: 0.0227721.
- Protected maximum drift: 0.0.
- Test suite: 20 tests passed.

The deterministic comparison is rendered in `experiment-0003-profile.svg`: black is target, dashed red is baseline, blue is candidate, and blue dots are editable semantic points.

## Next gate

Do not promote this result to `ACCEPT`. After a real commercial camera initializer passes, extract a consented side-view silhouette and semantic chin/jaw/neck anchors, lock its camera/crop, and replay the same one-variable baseline/candidate comparison. Geometry work beyond this local contour remains blocked until that result passes.
