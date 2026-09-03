# Experiment 0001 — camera projection baseline

Status: `TECHNICAL_CHECK_PASSED` (synthetic only), visual reconstruction remains `UNVERIFIED`.

## Visual target

From ordinary multi-angle photographs, recover a full-head model whose identity, frontal facial features, profile silhouette, ears, neck transition, and skin texture remain believable from held-out views.

## Evidence and unknowns

Published multi-view systems show that learned point maps and cameras followed by topology-aware fusion are a credible route. They do not prove commercial full-head parity on our inputs. Commercially usable full-head training data and the final dense correspondence model remain unverified.

## One variable

Camera projection recovery. The baseline uses normalized DLT on known 3D/2D correspondences. It is a convention and measurement reference, not a production camera initializer.

Prediction: exact synthetic observations should produce p95 reprojection error below 0.05 px. Falsification: any deterministic run above that limit blocks geometry work until the coordinate/model error is explained.

## Protected properties

Frontal identity, repaired facial features, profile/head silhouette, ear shape, UV layout, source texture, watertightness, manifold topology, triangle orientation, and absence of visible seams.

## Baseline, expected result, failure, rollback

- Baseline: no independent camera implementation.
- Expected: deterministic sub-pixel reprojection on the synthetic fixture.
- Failure: p95 error above 0.05 px or unstable result.
- Rollback: remove the DLT baseline; no geometry or texture candidate depends on it yet.

## Command and result

Run `headfoundry-camera-check`. The acceptance command and exact result are stored in normal test output; future real-image camera initializers must be evaluated against the same coordinate convention plus held-out landmarks.

