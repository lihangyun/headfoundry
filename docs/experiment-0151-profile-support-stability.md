# Experiment 0151: profile-envelope support stability

Status: read-only diagnostic `TECHNICAL_CHECK_PASSED`; anatomical
correspondence remains `UNVERIFIED`.

This experiment keeps the mesh, photographs and cameras unchanged and asks a
narrow question about experiment 0150: did its small numerical gain occur only
because the apparent contour jumped to unrelated mesh edges? For every sampled
right-profile nose, mouth and chin row, it compares the baseline envelope
support with the accepted tiny-camera support. It also reports continuous
surface motion under plus or minus two pixels of row jitter.

The first audit version incorrectly required all neighboring image rows to
share one literal triangle edge. That treats normal traversal across adjacent
triangles as instability; it is preserved locally and excluded. The corrected
rule checks only the camera perturbation under test and reports row jitter as a
continuous quantity.

All three nose, seven mouth and four chin samples retain a shared baseline-edge
vertex after the accepted camera step. Maximum surface-support shifts are
0.000102, 0.000124 and 0.000130 model units respectively. Therefore the small
0150 improvement is not an envelope-edge switching artifact. The row-jitter
spread is larger, especially at the lowest chin sample, but that does not prove
anatomical mismatch: adjacent pixel rows are expected to traverse the surface.

The deterministic support audit is `TECHNICAL_CHECK_PASSED`. It establishes
numerical contour continuity only; it cannot prove that a photographed outline
and a generic-mesh edge represent the same anatomical tissue. Anatomical
correspondence and KeenTools-level likeness remain `UNVERIFIED`.

Next gate: keep the cameras fixed and test a softly side-separated lower-face
shape family. Fit each pure profile on its visible hemisphere and require
transfer to the corresponding oblique outline, with the opposite side, eyes,
nose, chin and mesh safety protected. This directly tests whether limited
bilateral shape capacity—not camera or numerical support hopping—causes the
remaining side-profile error.
