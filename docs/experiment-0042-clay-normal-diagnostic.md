# Experiment 0042: distinguish flat-shading facets from geometry

Status: renderer invariance `TECHNICAL_CHECK_PASSED`; identity `UNVERIFIED`.
No geometry improvement, baseline promotion or quality parity claim.

The retained head was heavily faceted in the existing flat-normal renderer.
This experiment changes **only normal interpolation**, allowing inspection of
the coarse shape without confusing every triangle-lighting boundary with a
surface discontinuity. It does not move vertices, alter topology, smooth the
mesh, synthesize detail or project a photographic texture.

The existing CPU rasterizer gains an optional `smooth_shading=True` clay mode.
It computes area-weighted vertex normals, performs perspective-correct normal
interpolation and normalizes at each pixel. Lighting and two-sided convention
are unchanged. Degenerate interpolated normals fall back to the face normal.
The previous flat mode remains the default. Texture plus smooth clay mode is
rejected explicitly; there is no silent texture behavior change.

## Real-mesh check

Private evidence: `assets/private/subject-001/clay-normal-audit-v1/` contains
`comparison.png` and `report.json`; private runner `compare_clay_normals.py`.
Mesh SHA-256: `1d9b0a35f29f504af50343e3f52a3efca4eeec29a4662cf668ebc5459901a6be`.
All five fixed photo cameras from 0034 are reused. Consent/digests are validated;
no photo or biometric artifact is uploaded or committed.

The paired five-view sheet was inspected. The smooth view removes distracting
triangle lighting and reveals a coherent but generic, insufficiently matching
face. Eyes, nose/lips, ears and neck still need actual reconstruction work.
Smooth shading must not be interpreted as evidence of better geometry.

For every view, depth buffers and face-ID buffers are bit-identical between
flat and smooth rendering. Vertex arrays are exact. Thus rasterized visibility,
silhouette and triangle selection do not change; only RGB lighting changes.
Foreground counts are 33,501 / 37,633 / 45,665 / 37,794 / 43,838 respectively.
The short open-neck limitation from 0041 remains.

## Tests and next gate

63 tests pass. New checks exercise visibly different lighting on adjacent bent
triangles with identical depth/face IDs, input-vertex preservation, planar
agreement, and rejection of unsupported texture combination. Keep both flat
and smooth evidence for future geometry comparisons; never compare an old
flat render against a new smooth render as proof of shape improvement.

Next fit actual anatomical features/ears under the existing uncertainty and
protected-region checks. Independent cameras, subject likeness, eyes, texture,
UVs and finished exports are still incomplete.
