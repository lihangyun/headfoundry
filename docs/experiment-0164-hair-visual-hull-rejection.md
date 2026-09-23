# Experiment 0164: five-view hair visual hull

Status: local extraction and exact-camera replay `TECHNICAL_CHECK_PASSED`;
hair geometry and default promotion `REJECT`.

The unchanged experiment-0132 head, five photos and unaccepted cameras were
used throughout. A thresholded dark-hair mask from each photo constrained a
112 × 128 × 160 voxel visual hull. Voxels hidden behind the current head were
allowed so that a back-of-head bun could survive front-view occlusion. The
largest connected component contained 521,622 voxels. Only the hair geometry
changed; the original head OBJ was appended unchanged. The source OBJ/import
coordinate error was below 5.97e-8, and exact-camera Blender projection replay
p95 was below 0.0001 px in all five views.

The first mesh (17,612 vertices) roughly covered the crown, bun and nape, but
five-view photo overlays showed ridges, an above-ear slab, and implausible
rear-head surfaces. A controlled second mesh kept the *same occupancy* and
changed only Gaussian smoothing from 1 to 2.5 voxels and marching-cubes step
from 2 to 1 (62,731 vertices). The striping reduced, but the front still looks
like a rigid cap, the side has a horizontal above-ear seam, and the bun/nape
remain layered blocks. The left and right pure-profile views show the same
structural failure. Smoothing therefore does not repair the representation.

Mask agreement here would be self-evaluation against the same five photos
used to carve the volume. It cannot establish true hair geometry or likeness.
Both candidate OBJs, mask previews, occupancy and ten rendered views per
candidate remain in ignored local `assets/private/subject-001` only. No photo,
derived biometric artifact or local mask script is committed or uploaded.

Reject this visual hull for display/default use. The next hair representation
must explicitly constrain the scalp hairline, swept surface and gathered
connection, rather than treating all dark image pixels as a closed solid.
Camera acceptance, whole-head likeness and KeenTools-level quality remain
`UNVERIFIED`.
