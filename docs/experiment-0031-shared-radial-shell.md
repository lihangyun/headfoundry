# Experiment 0031: continuous experimental shell

Status: `REJECT` as a usable anatomical head; topology checks only pass.

A self-developed radial surface now fits the unchanged observed depth points
in the ray-camera world frame. For each height/angle bin, it uses median radius;
a neighbor regularizer and weak ellipsoidal prior fill unsupported bins. This
creates a single closed shell instead of overlapping sheets. It does **not**
yet directly fit photo silhouettes: observations remain learned depth estimates.
The requested photo-contour fitting step is still outstanding.

Private driver: `assets/private/subject-001/build_radial_shell.py`. Rights are
rechecked, source depth equality is asserted, and original retained depth-surface
vertices are transported through the ray cameras. Raw photos and prior outputs
are unchanged. No external template, weights or services were added.

Grid 64 by 96; 6,146 vertices including two inferred cap vertices; 12,288 faces.
4,884 of 6,144 radial bins have data. The remaining 1,260 bins (20.51%) use prior
and neighboring evidence. This is a bin count, **not an anatomical surface-area
coverage estimate**. All fitted bins are regularized; "observed" does not mean
ground-truth or untouched geometry. Prior-only vertex indices are recorded.

Private outputs: `radial-shell-v1/shell.obj`, `photo-comparison.png`, and
`radial-shell-orbit-v1/orbit.gif`. Photo comparisons use original ray-camera
projections. Faces touching prior-only vertices are tinted red. Originals remain
above, untextured mesh below. Both images and all seven orbit views were inspected.

Result: the shell is closed, but severe ridges/roughness, distorted cheeks,
incorrect side shape, absent proper ear/eye structure and inferred cap geometry
remain. The radial representation cannot express arbitrary overhangs or separate
anatomical parts. Closing a mesh has not established likeness or KeenTools parity.

53 tests pass, including two-face incidence for every shell edge, finite geometry,
explicit unsupported-region reporting and degenerate-data rejection. These do
not verify facial anatomy. The real visual candidate is rejected, not promoted.
Next directly constrain this experimental shared surface with photo contours;
retain uncertainty in cameras and mark any inferred anatomy.
