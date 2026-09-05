# Experiment 0008: photo-view raster diagnostic

Status: UNVERIFIED. Camera gate remains REJECT; no final geometry or texture
acceptance is implied by rendering an existing diagnostic face patch.

Implemented a NumPy CPU rasterizer with z-buffer occlusion, perspective-correct
pixel-space UV interpolation, bilinear sampling, and RGBA coverage through a
small OBJ preview command. No external renderer or proprietary service is used.
Near-plane crossing is rejected; it is not silently rendered incorrectly.

The existing baseline and candidate face patches were rendered under the same
three provisional cameras alongside the corresponding photographs. The primary
change is the diagnostic rendering path; meshes and cameras are unchanged.
The candidate additionally uses the frontal photograph as a fixed texture.
The texture is a one-view projection only, not multi-view fusion or recovered
albedo. Predicted frontal landmarks provide its UV coordinates.

The twelve-panel private comparison was generated and visually inspected.
Mouth, eye-corner, and outer-face alignment remain imperfect in intermediate
views. Frontal texture stretching is visible near the side boundary. Eye holes
are intentional missing geometry, not white eyeballs. This comparison makes
the limitations visible; it does not support a likeness-improvement claim.

Tests cover triangle-order-independent occlusion, perspective UV interpolation
against a hand-calculated value, uncovered pixels, and near-plane rejection.

```powershell
python tools/render_face_diagnostic.py <face.obj> <cameras.json> <new-preview.png> --view 1
```

Pillow is required for PNG output. This command does not change camera or mesh
status, and refuses to overwrite an output. Identity-specific artifacts remain
in ignored private storage. Next work remains camera/geometry consistency,
followed by full-head coverage and multi-view texture fusion with occlusion tests.
