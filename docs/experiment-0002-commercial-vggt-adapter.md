# Experiment 0002 — commercial VGGT camera adapter

Status: `TECHNICAL_CHECK_PASSED` (deterministic fixture only). Real checkpoint and visual reconstruction remain `UNVERIFIED`.

## One variable

Camera/point-map initialization contract. No head geometry or texture implementation changed.

Prediction: a deterministic five-view fixture in the official OpenCV camera-from-world convention passes matrix, rotation, focal, cheirality, focal-consistency, and cross-view reprojection gates. Corrupt matrices, negative-depth point maps, inconsistent tracks, and the non-commercial checkpoint identity must be rejected.

## Rights and checkpoint boundary

The accepted identity is exactly `facebook/VGGT-1B-Commercial` with license id `vggt-aup-license`, an actual local SHA-256, recorded accepting person/date, AUP review, and explicit non-military use. The gated file was not downloaded during this experiment. `facebook/VGGT-1B` cannot be selected as a fallback.

## Fixture and thresholds

- Five 1024x1024 views.
- Extrinsics: 3x4 OpenCV camera-from-world, x-right/y-down/z-forward.
- Intrinsics: canonical 3x3 pixel-space K.
- Point maps: per-view world-coordinate arrays.
- Cross-view tracks: shared world points and observed pixels.
- Cheirality: at least 95% positive depth.
- Reprojection p95: at most 3 px.
- Normalized focal spread: at most 0.25.

## Command and result

`C:\Python313\python.exe -m unittest discover -s tests -v`

Result on 2026-09-04: 17 tests passed. The deterministic VGGT fixture reported zero-pixel p95 reprojection error and `TECHNICAL_CHECK_PASSED`. Negative tests rejected missing biometric consent, non-commercial checkpoint identity, duplicate/blurry/incomplete views, malformed matrices, wrong coordinates, implausible focal length, negative-depth point maps, and inconsistent cross-view tracks.

## Decision and next gate

Keep the adapter. Do not start formal head geometry or texture work. The next gate is an authorized local installation of the commercial checkpoint followed by a 5–10 view consented or commercially cleared fixture run. It must emit the same matrix contract and pass all camera gates; otherwise status is `REJECT` and the failure is diagnosed at the camera layer.
