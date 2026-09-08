# HeadFoundry

HeadFoundry is a clean-room, quality-first multi-view 3D head reconstruction project. It does not reuse PeekSim code, KeenTools outputs, or proprietary service behavior.

The first milestone is deliberately narrow: prove that camera projection can be recovered and measured reliably before geometry or texture work is allowed to proceed. The repository contains a normalized-DLT reference, fail-closed rights/capture manifests, a commercial-VGGT output adapter, and camera-only quality gates.

## Current status

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
- Geometry reconstruction: architecture selected; implementation not yet started.
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
