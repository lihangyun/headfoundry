# Experiment 0106: local Apache MapAnything camera and observed surfaces

Status: local loading and coordinate conversion `TECHNICAL_CHECK_PASSED`;
raw inference report `UNVERIFIED`; camera gate and visual promotion `REJECT`.
No new accepted head, camera, texture or benchmark-parity claim.

## Question and fixed evidence

Can an independently trained dense-geometry initializer recover coherent
surfaces from the same five consented photographs, without the generic authored
head prior? The primary variable is initialization model. Images, original
coordinates and the frozen eleven LighterGlue held tracks are unchanged. No
track is removed or fitted in this image-only run. This tests one checkpoint
and inference configuration, not the feasibility of all learned geometry.

## Exact assets and execution

Only `facebook/map-anything-apache`, revision
`00f9c245bbcb60522d1ed7f9e9d88462c6e3f38a`, is enabled. Its official model card
declares Apache-2.0; the noncommercial default variant is excluded. The local
4,914,062,480-byte checkpoint verifies SHA-256
`fa06c0fdccefc5048e072c85935d5789b1e36b307f3859033c17f9dcb9fd5201`.
`examples/mapanything-apache-lock.json` records model/config/card hashes,
MapAnything and DINOv2 source revisions and tree/license hashes, UniCeption
source/license hashes and critical installed runtime versions.

`tools/run_mapanything.py` checks rights, capture metadata and asset identity
before loading. Local DINOv2 is architecture-only with `pretrained=False`;
the complete Apache checkpoint supplies encoder parameters. A narrow local
hub redirect rejects other repositories, architectures or encoder weights.
HF offline mode and a process network audit guard are enabled. There is no
VGGT or noncommercial fallback and no photo upload.

Actual execution uses existing Python 3.12, Torch 2.8.0 CPU FP32, six threads,
seed 17 and upstream 518-square resizing. This initial adapter rejects
non-square inputs and EXIF rotations. Memory-efficient inference uses
minibatch size one; AMP, edge/confidence filtering and multiview confidence
are disabled to retain raw evidence. Optional upstream UI/training features
are not installed or certified by this experiment.

Loading took approximately 20.4 seconds; five-view inference took 78.776
seconds. The output contains dense camera/world points, z depth, ray
directions, intrinsics, camera-to-world 4x4 poses and confidence/validity.
The model validity mask is not head segmentation. The tested rigid inverse
converts poses into OpenCV camera-from-world 3x4 matrices; transformed world
points agree with native camera points within the checked tolerance.

Local installation layout and execution (all third-party assets remain ignored):

```powershell
.venv\Scripts\python.exe tools\run_mapanything.py `
  assets\private\subject-001\run-manifest.json `
  assets\private\mapanything-source assets\private\dinov2-source `
  assets\private\mapanything-apache assets\private\subject-001\mapanything-apache-v1
```

Obtain the exact source revisions and the three model files named in the lock;
install its critical runtime versions in the local environment. The runner
rejects mismatched bytes and an existing output directory. This command
documents the completed run, not permission to overwrite its output.

## Camera result

All 33 leave-one-view-out third-view projections from the frozen eleven tracks
are retained. Their p95 is **48.5814 px**, with positive depth fraction 1.0:
`REJECT` against the unchanged 3 px threshold. The same frozen raw DA3 check
was 47.8225 px; this new raw initializer does not improve that measurement.
The previous best 7.5456 px is after joint refinement and must not be compared
as if it were an equivalent raw prediction.

The shared camera gate separately reports 47.6014 px p95; its source-pair
observations participate in triangulation, unlike the all-third-view metric
above. Matrix structure, rigid convention, finite values and positive depth
pass. The three checked normalized focal values span 4.7367 to 4.8718, above
the gate's 4.0 ceiling. No focal clipping or threshold relaxation is used.
Feature identity uncertainty remains; failure does not prove the photos unusable.

## Actual visual evidence

Each native point map was independently triangulated at stride three using
the existing ellipse mask and predicted validity, rejecting edges longer than
0.03 times median predicted depth. These are five separate open surfaces,
not a fused reconstructed head. Each has roughly 7,500–9,600 vertices.

The private comparison contains original photos, each surface in its own
camera, and the single frontal surface in all five predicted cameras. Own-view
patches show rough facial structure with ridges, holes and malformed profiles.
The same front patch shows severe stretched sheets/spikes in the other views.
Visual promotion is rejected. The audit does not isolate camera error, depth
error and boundary/masking artifacts; do not attribute the entire defect to
one of them or conceal it with texture/fusion.

Evidence remains under ignored private storage:

- Raw `mapanything-apache-v1/predictions.npz` SHA-256:
  `f78c9842f6b56e0019e71e72d33f2787cc7c52fce150ea108138b1f5d923dd85`.
- `mapanything-audit-v1/report.json` SHA-256:
  `5e4905f6bbb7aabc954775cfc90fbb6c825f56015d5a0ff38f354ead4f97bf51`.
- `mapanything-audit-v1/comparison.png` and five observed-surface OBJ files.

## Decision and next discriminating check

Do not fuse these raw patches or promote their cameras. First verify that
input conditioning can separate focal/camera uncertainty from dense depth
failure, keeping weights and photographs fixed. Any existing fitted camera
used as conditioning is itself unaccepted and cannot provide independent
validation. Require actual cross-view surface evidence, protected original
observations and the unchanged camera gate before claiming improvement.

The full public test suite passes 87 tests. New checks cover rigid pose
inversion, invalid frames, local architecture-only loading, missing rights,
wrong model identity and mismatched checkpoint bytes. Tests are not likeness
evidence. Implementation follows the minimal existing NumPy camera helpers
and renderer; no UI, service, training stack or new renderer was added.
