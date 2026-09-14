# HeadFoundry product status

Last updated: 2026-09-14 after experiment 0115.

## What exists

- A Python package under `src/headfoundry` with fail-closed rights/input manifests, camera conventions and gates, commercial-checkpoint adapters, depth/camera diagnostics, surface fitting, clipping, rasterization and profile diagnostics.
- Deterministic fixtures and regression tests under `tests`, plus pinned asset identities and example manifests under `examples`.
- A clean-room research trail in `docs`, including the governing ADR, claim/source ledger and numbered experiments.
- Experimental OBJ/head rendering on local authorized photographs. Private inputs and identity-derived artifacts stay under ignored local paths.
- GitHub repository: `https://github.com/lihangyun/headfoundry.git`, branch `main`.

## Current result

Experiments 0114–0115 produce a local closed-mouth replacement with an exactly shared boundary and unchanged retained head geometry. Geometry-aware interpolation substantially reduces artificial striping seen in the first patch. The actual mouth is closed, but the profile-only fit flattens the lower lip and worsens the left profile; full identity is still generic. Both candidates remain `REJECT` for promotion. This neutral patch removes the old cavity and does not support expressions or teeth.

Experiment 0113 tests a monotone vertical gap map directly on the smooth surface with fresh sampled contact heights. Actual frontal gaps narrow, but the side shape remains wrong and both profile means worsen. Half strength violates the triangle-area guard; stronger closure introduces corner-region intersections. Both candidates are `REJECT`. All 94 tests pass, but natural closure and recognizable identity remain unmet. Do not amplify this field or treat its continuous monotonicity as a collision certificate for the output mesh.

Experiments 0111–0112 reject a separately locked mouthClose target: sampled lip intersections occur even on the untouched base. A new independent Catmull-Clark helper produces actual smooth-surface meshes and five-view comparisons. Faceting decreases, but the mouth remains open/generic and the left profile worsens, so no refined mesh is promoted. The next shape fit must evaluate the smooth surface and re-establish its visible/contact support; post-fit smoothing alone is insufficient.

Experiments 0109–0110 locate the long exterior sheets in coarse-mask support and test an actual image-depth-driven head candidate. An inset skin patch excludes the sheets but is not a full head; camera metrics remain failed. The bounded candidate slightly improves the right profile while worsening the left and retains generic/open-mouth appearance. It is `REJECT`, not a visual improvement. All 88 public tests pass.

Experiment 0108 isolates ray representation without another model run: exact pinhole unprojection of unchanged depth makes own-view alignment exact, but dense transfer p95 remains 91.93 px and actual cross-view sheets persist. Candidate `REJECT`; native-ray approximation is not the sole cause. No camera, template or texture promotion.

Experiment 0107 tests one explicit uncalibrated 1800 px focal condition. The model does not enforce supplied intrinsics; camera p95 worsens to 51.48 px and visual promotion is `REJECT`. A new diagnostic finds 18–26 px own-view errors between native dense rays and their fitted pinhole cameras, despite correct rigid pose conversion. The optional conditioning path is tested; 88 tests pass, with no accepted visual improvement.

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

For the experimental closed-mouth patch, establish boundary tangent continuity and photo-consistent lip relief. Boundary positions alone do not prevent a visible transition, and profile-only fitting can erase a lip. Do not repeat the unconstrained three-depth-coefficient fit or accept on fitting cost alone.

Resolve the neutral mouth's surface/closure configuration with complete rim support on the evaluated surface and actual frontal/oblique/profile evidence before further identity fitting. Re-lift attachments after topology changes; never reuse old triangle IDs silently. Do not repeat two-point attraction, amplify mouthClose, or amplify the rejected depth-ray direction. Inset observed patches are not full heads and cannot establish camera accuracy. All camera, anatomy and visual acceptance gates remain unchanged.

## Known pitfalls

- A model or repository license does not automatically grant rights to every checkpoint or training dataset.
- Positive depth, valid matrices and lower reprojection error do not prove correct camera calibration or identity reconstruction.
- Shrinking internal lip gaps, valid triangle orientation and sampled no-crossing sections do not prove natural closure or full collision freedom.
- Actual photos and derived biometric/identity artifacts are local-only under the current consent and must not enter Git, PCR or public reports.
