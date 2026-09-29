# Experiment 0199: local single-image head initializer screen

Date: 2026-09-28–29. Execution checks `TECHNICAL_CHECK_PASSED`; actual facial
geometry and direct-head/donor promotion `REJECT`. Current head and cameras
remain byte-identical. This is a head-only screen, not hair or texture work.

## Asset decision and local execution

The official TripoSR source and pretrained model are explicitly MIT-released.
Use source revision `107cefdc244c39106fa830359024f6a2f1c78871` and only
`stabilityai/TripoSR` revision `5b521936b01fbe1890f6f9baed0254ab6351c04a`.
`examples/triposr-asset-lock.json` records exact source/license/model/config
hashes, attribution, local adaptations and runtime versions. It is an
experiment record, not an automatically enforced product manifest. Source and
model grants do not certify training-data rights or all dependency/binary
redistribution obligations. No paid/gated substitute is used.

Prepare one local front image using seeded OpenCV foreground segmentation and
uniform framing on a gray background; no generative repainting or online
background model. Keep observed foreground hair because deleting it would not
reveal the skull; evaluate only facial geometry. This input is not bare-head
ground truth. The five references remain independently generated/composited,
not one physically consistent capture. No additional subject consent is inferred.

Local adaptations load the checkpoint with `weights_only=True`, use only a
local DINO architecture JSON, disable rembg, and replace torchmcubes with CPU
scikit-image marching cubes. No separate DINO weights are downloaded. An
asymmetric ellipsoid control checks axis order and outward winding. Private
input rights and hashes are checked before inference. Offline model flags and
process-local socket denial are active before model import and image reading;
both runs record zero blocked network attempts. This is not an OS network
sandbox certificate. Images and all derived geometry remain local and ignored.

The initial private wrapper uses Python assertions for some checks; these
would disappear under `-O`. It records all source/package identities but does
not enforce every one before import. It must not be advertised as a production
fail-closed runner. The subsequent extraction control uses explicit exceptions
and verifies cached artifacts, full recorded Python source map, model/config,
license and declared runtime versions. Package metadata `torch==2.14.0` and
runtime build `torch.__version__==2.14.0+cpu` are different fields, now recorded
and checked separately. No runtime version was changed to pass.

## Actual output and one controlled extraction follow-up

One CPU inference with eight threads uses the prepared front image and default
density threshold 25. Load/forward/256 extraction take approximately
4.96/20.41/16.12 seconds. Preserve the inferred scene code. The only follow-up
changes the extraction grid to 512; it takes 131.89 seconds and does not repeat
image inference or change the learned field, threshold, weights or input.

| Audit | Grid 256 | Grid 512 |
| --- | ---: | ---: |
| Vertices | 74,837 | 309,329 |
| Triangles | 149,638 | 618,630 |
| Boundary edges | 0 | 0 |
| Edge-incidence records greater than two | 0 | 11 |
| Repeated-index / zero-area faces | 0 | 12 |
| Duplicate face extra copies | 0 | 1 |
| Edge-connected components | 12 | 20 |
| Largest component triangles | 149,354 | 616,810 |
| Trimesh watertight flag | true | false |

The 512 non-watertight flag is not evidence of an open hole: nine nonzero edges
have four incidences due to degenerate faces, and two collapsed self-loops have
six/ten incidences. The duplicate is a fully collapsed face. All anomalies are
in the main component; its 19 satellites have 1,820 faces in total. Marching
cubes permits degenerates and the existing Trimesh default merges vertices
without full validation; this is a plausible mechanism, not a proven stage
assignment because pre-Trimesh extraction arrays were not retained. No cleanup
is used to hide the failure. The 256 output is not a single clean anatomical
head simply because its components are closed.

Independent audit verifies 35 digests, including both outputs, cached code,
source/scripts, input/model identities and unchanged current head/cameras.
Chunked versus unchunked sampling at 16,391 points differs by at most 1.91e-6
in raw density; RGB preprocessing is exact. At one central-face section,
direct continuous density-root waviness remains before marching cubes or
Blender. This rules out an extraction-only explanation for that section, not
every artifact across the head.

## Real white-mesh result and stop decision

Render the raw source-space front and both sides without vertex color or
texture. The initial bright preview is followed by six matched clay renders:
same material, cameras, light transforms and exposure for both grids, verified
in the render record. Display exposure is reduced equally for both meshes;
this is inspection only. These are orthographic source-space views, not
registered photo-camera comparisons, so no relative likeness score is claimed.

Both actual meshes have slit-like eye anatomy, inaccurate nasal/lip shapes and
broad cheek/jaw corrugation. Grid 512 sharpens defects rather than supplying a
natural head. A labeled face-only comparison and a separate visual rejection
record retain this evidence locally. Do not substitute either mesh for the
current head, transfer its mouth as an anatomical donor, or polish this rejected
field through more resolution/threshold/texture sweeps. This rejects the tested
input/configuration, not all possible TripoSR outputs.

The next shape representation must preserve connected eyelid/nose/lip anatomy
and observed visible-contact support. A new candidate must improve actual front
and both-profile white meshes, not merely produce a closed object. Existing
camera, independent-reference, private-data and visual acceptance gates stay
in force. KeenTools-level quality remains `UNVERIFIED`.

## Verification and retained artifacts

The existing public suite passes 105 tests using the repository's `.venv`
Python, with `PYTHONPATH` pointing to `src`, and `-m unittest discover -s tests -v`.
The first attempt with the system Python could not import NumPy; reuse of the
already installed project environment resolves that environment failure without
changing tests or installing another package. These are library regressions,
not TripoSR quality tests. `git diff --check` passes.

Private evidence includes the original input-preparation and inference records,
cached scene code, both OBJ/NPZ meshes, source-space clay scene, six matched
extraction-control renders, labeled face-only comparison and visual rejection
record. None is included in Git. The public commit contains only this experiment,
source/rights/runtime identities and updated research/decision/status text.
