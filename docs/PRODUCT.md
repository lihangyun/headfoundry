# HeadFoundry product status

Last updated: 2026-09-12 after experiment 0106.

## What exists

- A Python package under `src/headfoundry` with fail-closed rights/input manifests, camera conventions and gates, commercial-checkpoint adapters, depth/camera diagnostics, surface fitting, clipping, rasterization and profile diagnostics.
- Deterministic fixtures and regression tests under `tests`, plus pinned asset identities and example manifests under `examples`.
- A clean-room research trail in `docs`, including the governing ADR, claim/source ledger and numbered experiments.
- Experimental OBJ/head rendering on local authorized photographs. Private inputs and identity-derived artifacts stay under ignored local paths.
- GitHub repository: `https://github.com/lihangyun/headfoundry.git`, branch `main`.

## Current result

Experiment 0106 completes actual offline Apache MapAnything inference on all five photographs in about 79 seconds on CPU. Its raw camera check is `REJECT` at 48.58 px held-out p95, focal plausibility fails, and observed-surface renders are not coherent across views. The asset-locked adapter and pose conversion run successfully; this is not an accepted head or visual improvement. The full public suite passes 87 tests.

Experiment 0105 executes standard and affine/domain-size-pooled SIFT with the same five photos and masks. Standard matching has no verified pair; the affine candidate has only one 26-inlier frontal/oblique pair, no profile connections and no recovered sparse model. Both reconstruction attempts are `REJECT`. The new runner preserves input rights and checks actual mask use; it does not establish accepted cameras.

The camera and full visual acceptance gates have not passed. Experiment 0104 verifies 44 additional CC0 nose/lip assets and tests a 32-control basis reduced to eight local directions. Aggregate profile and point fitting errors decrease under bounded step selection, with valid triangle and visibility checks, but actual five-view and enlarged mouth renders retain generic identity and an open/angular mouth. The numerical report remains `UNVERIFIED`; the candidate is `REJECT` for visual promotion. These fitting/selection metrics are not held-out validation. KeenTools-level parity remains `UNVERIFIED`.

## How to verify the public code

From `C:\workspace\headfoundry`:

```powershell
C:\Python313\python.exe -m pip install -e .
C:\Python313\python.exe -m unittest discover -s tests -v
C:\Python313\python.exe -m headfoundry.camera
C:\Python313\python.exe -m headfoundry.vggt tests\fixtures\vggt_camera_point_fixture.json
```

The repository is a library and experiment workspace, not a long-running service, so there is no start/stop procedure or deployment target. Publishing currently means committing reviewed public changes and pushing `main`; it does not publish private assets or constitute model-quality acceptance.

## Next gate

Diagnose the executed Apache MapAnything result by separating focal/camera uncertainty from dense depth and surface-boundary errors. A conditioning experiment may reuse existing unaccepted cameras, but those inputs cannot establish independent accuracy. Keep weights/photos fixed, preserve frozen validation and inspect real cross-view surfaces before any fusion or promotion. These failures do not establish that the photographs lack recoverable information.

## Known pitfalls

- A model or repository license does not automatically grant rights to every checkpoint or training dataset.
- Positive depth, valid matrices and lower reprojection error do not prove correct camera calibration or identity reconstruction.
- Shrinking internal lip gaps, valid triangle orientation and sampled no-crossing sections do not prove natural closure or full collision freedom.
- Actual photos and derived biometric/identity artifacts are local-only under the current consent and must not enter Git, PCR or public reports.
