# Experiment 0165: anatomical crop of the rejected hair hull

Status: local candidate generation and exact-camera replay
`TECHNICAL_CHECK_PASSED`; hairstyle and default promotion `REJECT`.

This follow-up preserves experiment 0164's photos, threshold masks, saved
occupancy, base head and five locked but unaccepted cameras. The sole geometry
change restricts the existing occupancy to upper scalp (world Y < -0.42) or
rear bun (world Z > 0.92 and Y < 0.10). The largest retained component has
345,085 voxels and produces 43,004 hair vertices with the same 2.5-voxel
smoothing and unit marching-cubes step as experiment 0164's second mesh.
World Y points downward in the locked camera frame, and Z points toward the
back of the head.

Exact-camera Blender source import differs from the OBJ by less than 6e-8
model units; separate clay and photo overlays were rendered for all five
views. Removing lower rear voxels makes the previous layered nape blocks
disappear. It also exposes a horizontal scalp cut and leaves a disconnected
looking, rectangular bun connection. The front retains a rigid cap. Both
pure-profile photo overlays are less plausible than the subject's smoothly
gathered hair. The unchanged face remains generic, so no whole-head or
side-profile identity improvement is established.

This discriminates a meshing artifact from a representation failure: stronger
smoothing and an anatomical crop each remove some local artifacts, but a
closed solid carved from dark photo masks cannot express the required hairline,
scalp layering and sweep into the bun. Stop this visual-hull branch. The local
candidate OBJ, five-view diagnostic and source occupancy remain ignored in
`assets/private/subject-001`; no photos or derived biometrics are committed.
Next use an explicit scalp surface and gathered-flow representation, with
five-view visual acceptance independent of the same masks used to fit it.
