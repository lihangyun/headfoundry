# HeadFoundry

HeadFoundry is a clean-room, quality-first multi-view 3D head reconstruction project. It does not reuse PeekSim code, KeenTools outputs, or proprietary service behavior.

The first milestone is deliberately narrow: prove that camera projection can be recovered and measured reliably. Later user authorization permits unaccepted experimental geometry while that gate remains failed; it does not waive acceptance. The repository contains a normalized-DLT reference, fail-closed rights/capture manifests, a commercial-VGGT output adapter, and camera quality gates.

## Current status

- Experiment 0070 adds a tested fixed-camera graphical-target point fitter with explicit eligibility masks and per-point pixel scales. It does not estimate uncertainty or claim visual improvement; real-photo integration and contour checks remain required. Full suite: 75 tests.
- Experiment 0069 triangulates the visible alar pairs without a mesh prior: several-pixel disagreement remains, and recovered offsets are sensitive to assumed 3px input perturbations. Do not convert these detector pairs directly into exact geometry targets; no model/camera promotion.
- Experiment 0068 adds nasal-base vertical control. Frontal alar error decreases, but left-oblique and both nasal profile errors increase; actual five-view comparison does not justify promotion. Original model/cameras stay unchanged.
- Experiment 0067 verifies visible alar support and adds twelve frontal/near-oblique nasal observations. Far-side occluded points are excluded. The fitted candidate still regresses frontal alar and left profile evidence; no promotion. Alar-base vertical support is the next specific question.
- Experiment 0066 prepares six pinned CC0 nasal controls and fits a three-parameter bilateral nose trial. Changes are tiny and left nasal error increases; actual five-view inspection does not support promotion. Frontal/oblique nasal anatomy remains insufficiently constrained.
- Experiment 0065 verifies candidate canthi before/after contour-supported pose fitting, including profile visibility. Same-support camera gains are negligible and actual profiles remain visually unchanged; no promotion. Nose/lip anatomy remains unresolved.
- Experiment 0064 finds four nearby canthus correspondence candidates visible in all three fitting views, with lower projection error and inspected photo/clay crops. Geometry and cameras are unchanged; profile support, pose impact and anatomical accuracy remain unverified.
- Experiment 0063 adds profile arcs to screened pose fitting, restraining the right pose drift and lowering fitted profile errors. Retained anchor errors increase, and actual views remain generic. Both contour and anchors are now training inputs; no camera or likeness acceptance.
- Experiment 0062 applies the three anchor exclusions and reruns fixed-focal pose fitting. The right pose visibly drifts away from the photo and profile MAE worsens to 17.34px despite smaller retained-point error. Candidate rejected; reliable side-view support is still required.
- Experiment 0061 identifies concrete anchor conflicts: the right-profile detector nose target is outside the photo silhouette, and two fitted oblique mouth anchors are self-occluded on the current mesh. Non-destructive rejection guidance and numbered photo/clay crops are retained; original data and cameras stay unchanged.
- Experiment 0060 rejects four fixed-shape focal/pose candidates: some training anchor errors decrease, but both profile checks regress versus the original cameras. Actual bilateral views were inspected; focal is still uncalibrated, and anatomical anchor correspondence is the next audit.
- Experiment 0059 fits four whole-head controls to frontal/oblique outlines and anchors. Outline fitting errors decrease, anchors slightly regress, and bilateral profile errors stay essentially unchanged. Actual five-view comparison still lacks likeness; the candidate is unverified and not promoted.
- Experiment 0058 adds four pinned CC0 whole-head shape assets and inspects actual fixed-camera scope previews. They affect skull/face/jaw proportions but barely change the nose/lip profile; subject fitting and visual improvement remain unverified. Preparation supports an explicit reviewed target lock.
- Experiment 0057 rejects authored lip-height/position fitting: mouth-point error decreases but both side profiles regress. Additional CC0 target assets are separately locked; broader face-shape coverage is the next investigation, not repeated lip-only adjustments.
- Experiment 0056 fits the authored mouth-volume assets to actual multi-view inputs. Small fitting-error decreases and valid local triangle checks do not establish visible likeness; the candidate stays unverified. Lip height/position remains a separate next question.
- Experiment 0055 prepares six hash-pinned CC0 mouth/philtrum shape targets with independent sparse-data parsing and exact source-ID mapping. Generic previews were inspected; fitting these targets to the subject is next. No identity acceptance; 71 tests pass.
- Experiment 0054 tests six smooth lip modes: right fitting error improves only with left regression; per-point left protection yields an effectively unchanged mesh. Neither candidate is promoted. An anatomically structured shape basis is the next avenue, not larger ad hoc lip updates.
- Experiment 0053 lowers bilateral local lip fitting error while preserving protected projections, but actual clay views show unacceptable lip protrusions. Candidate rejected for visual promotion; further identical vertexwise iterations are not the next step.
- Experiment 0052 identifies scanline correspondence switching from chin to neck and adds a tested ordered-curve distance diagnostic. Translation-only candidates still regress chin/anchor alignment and are rejected; no camera promotion. Full suite: 69 tests.
- Experiment 0051 reduces the right-profile fitting MAE from 8.03 to 7.12 px while preserving frontal vertex projections and all 426 sampled left-profile rows. Actual photo overlays still show nose/lip defects; the candidate remains unverified and is not promoted.
- Experiment 0050 adds occlusion-preserving component filtering to surface lifting. On the actual combined head it explicitly rejects 18 eye-helper hits as body observations, including all five previously audited eye mismatches. Anatomical correctness remains unverified; 67 tests pass.
- Experiment 0049 adds an explicit, non-default CC0 eye-helper preparation option, verified on the pinned asset and rendered in all five views. Generic eye surfaces now have a local experimental output; subject-specific eyes and likeness remain unverified. Full suite: 66 tests.
- Experiment 0048 confirms substantial cross-view drift in clay-derived bridge/nose correspondences on the exact same unchanged head. These mappings remain unverified and must not be treated as anatomical truth for stronger deformation.
- Experiment 0047 rejects a dense pose-only candidate: detector residuals decrease but manual-anchor alignment worsens in all three fitted views. Cameras are not promoted; central anatomical correspondence support must be resolved before stronger deformation.
- Experiment 0046 reruns dense fitting with screened eye support. On identical corrected evaluation support, held p95 is unchanged versus 0044 (23.0857 px); no clear visual improvement or baseline promotion. The largest remaining held residuals include exactly frozen central points, requiring a correspondence/camera diagnosis before relaxing profile protection.
- Latest audit 0045 identifies internal eye-surface hits masquerading as eyelid correspondences. A five-point, correspondence-only rim proposal reduces large oblique errors without changing the mesh. It remains `UNVERIFIED`; unrestricted anatomical use of raw clay hits is rejected. See the experiment before repeating dense deformation.
- Latest experiment 0044: dense triangle-correspondence fitting runs on the actual five-photo subject; held detector-point p95 decreases from 26.56 to 23.49 px, but visual likeness remains unverified and left profile MAE slightly worsens. No baseline promotion. Full suite: 65 tests.
- Product/technical research: complete enough to select an architecture.
- Camera projection baseline: implemented and covered by deterministic synthetic tests.
- Weight-independent perspective landmark solver: implemented; first real-photo held-out camera check is `REJECT` (39.35 px p95). See experiment 0005. Install `.[geometry]` for this optional solver.
- Commercial VGGT adapter: local output contract and asset lock implemented; real gated checkpoint execution is `UNVERIFIED`.
- Input rights and capture validation: implemented; missing consent, provenance, license, file hash, view coverage, resolution, or clarity evidence is `REJECT`.
- Side-profile contour fitting: deterministic jaw/chin/neck slice is `TECHNICAL_CHECK_PASSED`; real-photo improvement is `UNVERIFIED`.
- Real-photo face-patch diagnostics: OBJ export and CPU depth/texture rendering work; these are not full heads and use cameras that still fail validation. Experiments 0007–0008 document visible limitations.
- Dense camera diagnostic: 60 held-out points yield 10.44 px p95, still `REJECT`; see experiment 0009. No full-head or side-profile quality acceptance.
- Convergence audit: extending to 60 iterations yields 9.73 px, still `REJECT`; experiment 0010 includes a shape-independent epipolar check and inspected photo overlays.
- Shape-independent calibrated initialization: implemented and synthetically tested; real-photo candidate rejected (experiment 0011). Positive depth does not imply correct calibration.
- Nonlinear pair-pose refinement: implemented; fixed-focal pair errors improve, but the prior-free three-view held-out reprojection remains `REJECT` at 11.80 px (experiment 0012).
- Correspondence audit: no independent three-view texture tracks found in the bounded masked-SIFT check; manual physical-landmark verification is next (experiment 0013). This does not establish that the photos are unusable.
- Independent visual reading: six anatomical anchors checked against fixed cameras; p95 8.23 px with material reading uncertainty, still `UNVERIFIED` (experiment 0014).
- Optional XFeat local extraction: pinned source/weight/consent checks implemented; sparse three-view track candidate remains `REJECT` (experiment 0015). No VGGT checkpoint substitution.
- XFeat fine matching: one strict three-view cycle; symmetric endpoint refinement gives zero. Insufficient support for camera acceptance (experiment 0016).
- LighterGlue local matcher: locked checkpoint and Kornia 0.8.1 loader implemented. A frozen 40-train/11-held-track joint camera fit yields 7.5456 px held-out p95, still `REJECT` (experiment 0017).
- Robust camera initialization: explicit training-only consensus, duplicate/intrinsic/low-parallax guards and synthetic outlier tests implemented; these do not diagnose the real-photo failure.
- DA3-BASE: pinned local CPU inference and depth/camera conversion implemented; all five photos executed. Same-track joint refinement yields 7.5485 px held-out p95, still `REJECT`; no measured final-alignment improvement over the previous initializer (experiment 0018). Current full suite: 43 tests.
- Correspondence localization: all eleven held tracks visually inspected; a bounded bidirectional translation tracker retains no held-out tracks and is not adopted (experiment 0019). No validation points were removed to obtain a pass.
- Local affine matching also supplies zero fully consistent three-view replacement tracks (experiment 0020). High patch similarity alone is not treated as physical point agreement.
- Geometry reconstruction: experimental anatomical template fitting and mesh export implemented; subject likeness and production acceptance remain incomplete.
- Texture fusion: architecture selected; implementation not yet started.
- KeenTools-level visual parity: **UNVERIFIED**. No claim is made until the complete acceptance suite passes.

## Quick start

```powershell
cd C:\workspace\headfoundry
C:\Python313\python.exe -m pip install -e .
C:\Python313\python.exe -m unittest discover -s tests -v
C:\Python313\python.exe -m headfoundry.camera
C:\Python313\python.exe -m headfoundry.vggt tests\fixtures\vggt_camera_point_fixture.json
C:\Python313\python.exe -m headfoundry.profile examples\profile_fixture.json --svg docs\experiment-0003-profile.svg
C:\Python313\python.exe -m headfoundry.manifest path\to\run-manifest.json
C:\Python313\python.exe -m headfoundry.quality examples\quality_manifest.json
```

The VGGT fixture check must report `TECHNICAL_CHECK_PASSED`; this proves the adapter and matrix conventions, not the real checkpoint or visual quality. `examples/run-manifest.template.json` documents the required asset fields and intentionally fails until its placeholders are replaced with actual files, hashes, rights, and consent. Manifests may be limited to `local_head_reconstruction_validation`; every input's `allowed_uses` must match the declared purpose, so local consent cannot be expanded to commercial use. The example quality manifest intentionally fails later-stage gates.

## Commercial checkpoint installation

Only `facebook/VGGT-1B-Commercial` with license id `vggt-aup-license` is accepted. The original `facebook/VGGT-1B` is rejected even if it is locally available.

1. An authorized person reviews and accepts the gated model terms at [facebook/VGGT-1B-Commercial](https://huggingface.co/facebook/VGGT-1B-Commercial). HeadFoundry does not automate acceptance.
2. Download `model.safetensors` through the authenticated Hugging Face web UI or CLI into `assets/private/VGGT-1B-Commercial/`. This directory is git-ignored.
3. Compute its SHA-256, copy `examples/run-manifest.template.json`, and record the exact path, digest, accepting person/date, license id, AUP review, and non-military use declaration.
4. Run `python -m headfoundry.manifest <manifest>`. Any missing or mismatched field is `REJECT`; there is no fallback checkpoint.

The separate free-commercial DA3-BASE candidate has its own locked local runner,
not a VGGT fallback. See [installation and measured limits](docs/experiment-0018-da3-base.md#reproduction).

## Project documents

- `docs/report-source.md`: canonical technical research report.
- `docs/claim-source-ledger.md`: claim-to-source audit trail.
- `docs/adr/0001-quality-first-reconstruction.md`: architecture decision.
- `docs/experiment-0001-camera-baseline.md`: first falsifiable experiment record.
- `docs/experiment-0002-commercial-vggt-adapter.md`: commercial checkpoint adapter and deterministic camera-gate record.
- `docs/experiment-0003-profile-contour.md`: bounded side-profile contour experiment and next real-image gate.
- `docs/experiment-0017-lighterglue-camera.md`: locked local matching, whole-track validation, robust initialization guards and rejected joint camera fit.
- `docs/experiment-0018-da3-base.md`: explicit free-commercial local camera/depth candidate, frozen observations and rejected refinement.

## Legal boundary

KeenTools Cloud is used only as a publicly documented product-quality reference. Its service, private sessions, generated outputs, and implementation are not used as training material, reverse-engineering inputs, or automated competitive benchmarks.
# Latest experimental geometry (2026-09-08)

[Experiment 0043](docs/experiment-0043-clay-surface-correspondence.md) establishes
an experimental detector-to-clay correspondence route: 464 exact visible surface
hits, four explicit misses. Projection correctness is tested, anatomical accuracy
is not accepted. Current suite: 64 tests.

[Experiment 0042](docs/experiment-0042-clay-normal-diagnostic.md) adds optional
smooth-normal clay inspection alongside the unchanged flat default. Five-view
depth/visibility buffers are exact; this changes lighting, not geometry or
likeness. Current suite: 63 tests.

[Experiment 0041](docs/experiment-0041-planar-neck-termination.md) removes the
irregular shoulder crop with exact shared-edge plane clipping, preserving
retained facial coordinates. The short neck remains open and generic; this is
not likeness acceptance. Current suite: 62 tests.

[Experiment 0040](docs/experiment-0040-cheek-protection-support.md) confirms that
an oversized protected rectangle froze oblique cheek constraints. A bounded
feature-ring experiment reduces those fitting errors with frontal projection
and central-profile regression checks intact; likeness is still unverified.

[Experiment 0039](docs/experiment-0039-photo-oblique-boundaries.md) records
original-photo oblique boundary readings independent of model projection.
The resulting bounded geometry change is negligible and not adopted; protected
cheek support and camera uncertainty require review before further fitting.

[Experiment 0038](docs/experiment-0038-oblique-jaw-rejection.md) rejects a
far-side detector-oval fit: those points are not the visible oblique silhouette.
No new geometry baseline is adopted. Independent boundary evidence is needed
before repeating oblique fitting; the full reconstruction remains incomplete.

[Experiment 0037](docs/experiment-0037-lower-face-outline.md) fits lower cheek/jaw
width with protected facial features. A rear-neck contour-confound trial was
rejected; the corrected face-ROI experiment has inspected five-view evidence but
no accepted likeness. Current suite: 60 tests.

[Experiment 0036](docs/experiment-0036-continuous-profile.md) fits continuous
projected edge positions with perspective-correct weights. Both profile fitting
residuals decrease while frontal vertex projections stay fixed; full likeness
remains unverified. Current suite: 60 tests.

[Experiment 0035](docs/experiment-0035-frontal-protected-profile.md) adds local
profile depth fitting that preserves frontal vertex projections. Fixed-camera
five-view evidence exists; profile fitting residuals decrease but likeness is
still unverified. Current suite: 58 tests.

[Experiment 0034](docs/experiment-0034-anatomical-template-pose.md) places the
unchanged anatomical template in all five photos and provides actual clay and
overlay comparisons. Pose is experimental, shape is still generic; no likeness
or camera acceptance. Current suite: 56 tests.

[Experiment 0033](docs/experiment-0033-cc0-head-prior.md) installs a pinned CC0
MakeHuman head/neck template without its AGPL program code. It provides a coherent
anatomical starting mesh; it is **not yet fitted to the subject**.

[Experiment 0032](docs/experiment-0032-photo-profile-step.md) directly applies
approximate photo-profile constraints to the shared mesh and provides fixed-camera
before/after evidence. Coarse head shape remains visibly rejected.

[Experiment 0031](docs/experiment-0031-shared-radial-shell.md) creates a single
closed experimental shell and original-photo comparison with inferred regions
marked. The visible shape remains rejected; direct photo-contour fitting is pending.

[Experiment 0030](docs/experiment-0030-affine-depth.md) tests a bounded depth
offset. Held error changes only marginally and the active camera bound remains;
the candidate is rejected, with experimental shared-surface work next.

[Experiment 0029](docs/experiment-0029-active-bound.md) identifies opposing depth
and pixel gradients at the active camera bound. Parameters and held error are
unchanged; the diagnostic does not justify widening constraints or acceptance.

[Experiment 0028](docs/experiment-0028-joint-pixel-depth.md) adds joint image/depth
constraints. Held projection reaches 8.82 px, but a bound is active and depth
consistency slightly regresses. The candidate is not accepted.

[Experiment 0027](docs/experiment-0027-depth-camera-registration.md) adds bounded
joint depth/camera registration. Held error drops from 25.76 to 11.66 px, still
failing the gate; profiles and complete-head quality remain unverified.

[Experiment 0026](docs/experiment-0026-ray-camera.md) tests DA3's alternate ray
camera path with identical depth arrays. Unrefined prediction errors decrease,
but the camera gate still fails; no accepted head or quality parity is claimed.

[Experiment 0025](docs/experiment-0025-depth-sampling.md) provides a fixed-frame
nearest/bilinear comparison. Large seams persist; substantial cross-view depth
conflicts remain. Sampling changes do not establish likeness improvement.

[Experiment 0024](docs/experiment-0024-free-space-fusion.md) retains free-space
evidence during fusion. Boundary count decreases, but visual seams persist;
the result is still rejected as a usable head.

[Experiment 0023](docs/experiment-0023-projective-fusion.md) implements and tests
shared depth fusion. The real-subject candidate is rejected for visible cracks
and noise; it does not establish side-profile improvement.

[Experiment 0022](docs/experiment-0022-common-frame-orbit.md) adds a common-frame
orbit and OBJ union. Rotation exposes substantial overlapping-sheet errors;
this is an inspection artifact, not a fused/accepted head.

User-authorized, unaccepted depth-surface exports now exist locally. See
[experiment 0021](docs/experiment-0021-observed-depth-surfaces.md) for the actual
five-view clay comparison, limitations and counts. These are separate open
surfaces, not a complete head; camera acceptance and visual quality remain unmet.
