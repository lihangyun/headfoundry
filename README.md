# HeadFoundry

HeadFoundry is a clean-room, quality-first multi-view 3D head reconstruction project. It does not reuse PeekSim code, KeenTools outputs, or proprietary service behavior.

The first milestone is deliberately narrow: prove that camera projection can be recovered and measured reliably before geometry or texture work is allowed to proceed. The repository already contains a runnable normalized-DLT camera estimator and a fail-closed quality-gate CLI.

## Current status

- Product/technical research: complete enough to select an architecture.
- Camera projection baseline: implemented and covered by a deterministic synthetic test.
- Geometry reconstruction: architecture selected; implementation not yet started.
- Texture fusion: architecture selected; implementation not yet started.
- KeenTools-level visual parity: **UNVERIFIED**. No claim is made until the complete acceptance suite passes.

## Quick start

```powershell
cd C:\workspace\headfoundry
C:\Python313\python.exe -m pip install -e .
C:\Python313\python.exe -m unittest discover -s tests -v
headfoundry-camera-check
headfoundry-quality examples\quality_manifest.json
```

The camera check must report sub-pixel reprojection error. The example quality manifest intentionally fails several later-stage gates, demonstrating that incomplete work cannot be presented as a successful reconstruction.

## Project documents

- `docs/report-source.md`: canonical technical research report.
- `docs/claim-source-ledger.md`: claim-to-source audit trail.
- `docs/adr/0001-quality-first-reconstruction.md`: architecture decision.
- `docs/experiment-0001-camera-baseline.md`: first falsifiable experiment record.

## Legal boundary

KeenTools Cloud is used only as a publicly documented product-quality reference. Its service, private sessions, generated outputs, and implementation are not used as training material, reverse-engineering inputs, or automated competitive benchmarks.

