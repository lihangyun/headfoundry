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

## Project documents

- `docs/report-source.md`: canonical technical research report.
- `docs/claim-source-ledger.md`: claim-to-source audit trail.
- `docs/adr/0001-quality-first-reconstruction.md`: architecture decision.
- `docs/experiment-0001-camera-baseline.md`: first falsifiable experiment record.
- `docs/experiment-0002-commercial-vggt-adapter.md`: commercial checkpoint adapter and deterministic camera-gate record.
- `docs/experiment-0003-profile-contour.md`: bounded side-profile contour experiment and next real-image gate.

## Legal boundary

KeenTools Cloud is used only as a publicly documented product-quality reference. Its service, private sessions, generated outputs, and implementation are not used as training material, reverse-engineering inputs, or automated competitive benchmarks.
