# HeadFoundry product status

Last updated: 2026-09-12 after experiment 0102.

## What exists

- A Python package under `src/headfoundry` with fail-closed rights/input manifests, camera conventions and gates, commercial-checkpoint adapters, depth/camera diagnostics, surface fitting, clipping, rasterization and profile diagnostics.
- Deterministic fixtures and regression tests under `tests`, plus pinned asset identities and example manifests under `examples`.
- A clean-room research trail in `docs`, including the governing ADR, claim/source ledger and numbered experiments.
- Experimental OBJ/head rendering on local authorized photographs. Private inputs and identity-derived artifacts stay under ignored local paths.
- GitHub repository: `https://github.com/lihangyun/headfoundry.git`, branch `main`.

## Current result

The camera and full visual acceptance gates have not passed. Experiment 0102 dynamically rematches visible lip-seam constraints and lowers fixed-support error, but loses three originally visible oblique supports and fails enlarged visual inspection: the mouth remains angular and the identity generic. The candidate is `REJECT` for promotion. KeenTools-level parity remains `UNVERIFIED`.

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

Stop fitting the provisional central lip-rim samples to nearest photo-curve points. The next geometry experiment must use a more expressive anatomical boundary/surface representation or target broader high-impact identity shape. Preserve fixed-support reporting and inspect actual five-view renders, especially both profiles, before any promotion.

## Known pitfalls

- A model or repository license does not automatically grant rights to every checkpoint or training dataset.
- Positive depth, valid matrices and lower reprojection error do not prove correct camera calibration or identity reconstruction.
- Shrinking internal lip gaps, valid triangle orientation and sampled no-crossing sections do not prove natural closure or full collision freedom.
- Actual photos and derived biometric/identity artifacts are local-only under the current consent and must not enter Git, PCR or public reports.
