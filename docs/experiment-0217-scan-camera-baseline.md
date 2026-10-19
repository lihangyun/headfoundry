# Experiment0217: scan-assisted camera baseline on real-case-001

Date: 2026-10-19. Implemented checks: `TECHNICAL_CHECK_PASSED`.
The pre-registered camera screen is `REJECT`; geometry fitting did not follow.

The user confirms both real cases use millimeter STL coordinates and video/scan
from the same stage without intervening face-shape changes. A private supplement
binds this statement to the original0216 manifest; original intake is preserved.
These are user-confirmed metadata, not scanner calibration or expression proof.

## Bounded hypothesis

Visual target: project the supplied, unchanged skin scan into the development
video and inspect nose/cheek/chin placement in frontal and bilateral oblique
frames. This establishes whether the new paired data can support measurement.
It is explicitly scan-assisted calibration, not photo-only head reconstruction.

Primary variable: camera alignment. Skin geometry stays exactly as provided.
Counter-evidence: closed scan eyes, possible expression/pose differences and
learned landmark bias on untextured scan renders can invalidate correspondences.

First extract the existing hash-locked Apache MediaPipe observations on an
upright scan preview and the16 already decoded development frames. Inspect
surface hits and facial point placement. Detector relative depth is excluded.
If landmark support is unusable, stop this proposed automatic association before
camera fitting; do not tune rendering or silently replace labels to get a pass.

If support is usable, test one shared square-pixel focal model with centered
principal point and zero distortion. Fit per-frame rigid pose against the fixed
scan anchors. Declare landmark training/validation slots and usable frames before
fitting. Pure-profile predictions remain outside the prior detector's documented
80-degree range and cannot establish calibration by themselves.

Predict visible scan alignment on neutral front/oblique frames. A first diagnostic
screen requires positive scan depth, a proper rotation, focal length inside the
declared search range without a bound hit, validation landmark p95 below3px and
actual scan/photo projection review. This is a development screen, not calibrated
product acceptance or independent physical-camera truth. A failed screen stops
geometry fitting on these cameras; no focal/mask/slot sweep follows.

Protected properties: source scan coordinates/topology, the original intake,
case002 reserved from fitting, and existing head/camera defaults. No bone-based
skin inference, training, data upload, hair or texture work.

Source-only baseline:0216 intake sheets. Candidate evidence must include exact
pose/intrinsic matrices, provenance, held-slot errors and scan overlays. Numeric
checks alone cannot pass the visual gate. A successful screen would permit a
separately declared geometry experiment; it would not complete HeadFoundry.

## Fixed first-run settings (before fitting)

Use development frames0,208,277,555,832 to estimate a shared focal length.
Frames624 and1040 are excluded from focal fitting; estimate only their nuisance
rigid poses after freezing focal length. These frames come from one video and
are not statistically independent subjects. Camera training slots are
`[33,263,61,291,168,4,98,327]`; validation slots are
`[133,362,6,1,2,0,17,152]`. All were absent from the camera-fit objective except
the declared training set; their detector estimates are not anatomical truth.
Chin slot152 is especially view dependent and remains diagnostic.

Fit one focal value inside[400,3000] pixels, initial1000, principal point(360,640),
no distortion/aspect optimization, soft-L1 scale2px, at most200 function
evaluations. Use exact orthographic first-hit lifting of the original frontal
scan-render pixels to obtain provisional scan surface anchors. Every selected
anchor must hit and replay below1e-6px. No scan-landmark adjustment, failed-view
substitution, label tuning, shape deformation or focal sweep is permitted in
this screen. Eye closure and source-render domain bias remain explicit risks.

## Executed result and stop

The locked detector found one face in the scan preview and12/16 sampled video
frames. Four samples, including near-profile views, had no face. The declared
front/oblique frames were retained exactly; no failed frame was substituted.

All16 declared scan anchors hit the original surface. Exact orthographic lifting
replays to1.14e-13px. The one camera fit converges in43 evaluations (about3.96s,
including checks), shared focal2879.48px, with proper rotations and positive
whole-scan depths. These facts verify computation, not physical calibration.

| Frame | Used for focal fit | Training mean px | Validation p95 px |
| --- | --- | --- | --- |
| 0 | yes | 4.043 | 17.963 |
| 208 | yes | 3.170 | 22.380 |
| 277 | yes | 4.474 | 13.040 |
| 555 | yes | 2.182 | 16.933 |
| 832 | yes | 5.084 | 10.463 |
| 624 | no, nuisance pose only | 5.017 | 7.068 |
| 1040 | no, nuisance pose only | 5.582 | 11.886 |

Every frame misses the3px diagnostic gate. Frame208's fixed outer-eye slot263
also lies2.09mm behind the actual visible scan surface, failing training-support
visibility. The screen is rejected without focal, label, rendering or shape
parameter sweeps. Case002 remains excluded from fitting.

Seven unchanged-source scan renders were generated for diagnosis. Actual Blender
projection replay is at most0.000504px. The three-row front/oblique sheet was
visually inspected: source scan and video show broadly consistent face placement,
but closed scan eyes, facial feature offsets and imperfect jaw placement remain.
The white mesh is the user's supplied scan; it is **not a photo-reconstructed
candidate**, and source-only overlays do not constitute acceptance.

A read-only per-slot breakdown on these same frozen poses finds mean outer-eye
slot33/263 errors7.75/8.56px, mouth slot0 error11.54px, chin slot152 error14.47px,
and bridge slot6 error2.05px. Several chin anchors become occluded by roughly
10-12mm in the known scan. This supplies evidence of a correspondence/visibility
problem; it does not identify all residuals as camera error, validate remaining
slots, justify dropping difficult validation labels or change the failed gate.

Next obtain independently fixed anatomical scan/image correspondences and
distinguish material points from view-dependent contours before another camera
hypothesis. Review and lock any such annotations **before** fitting. Preserve this
result; do not optimize shape to compensate for its unreliable associations.

## Reproduction and evidence

```text
python tools/observe_real_capture_0217.py
python -m unittest tests.test_scan_camera_baseline -v
python tools/calibrate_scan_camera_0217.py
blender --background --python tools/render_scan_camera_0217.py
python tools/render_scan_camera_0217.py --assemble
python -m unittest discover -s tests
```

Existing outputs refuse overwrite. All135 public tests pass. Synthetic checks
independently verify nearest-layer orthographic lifting/display roll and metric
PnP recovery. Actual data, matrices, scan triangle attachments, hashes, point
overlays and the source-only review remain in the ignored private pilot under
`camera-baseline-0217/`. The original intake and its hashes are unchanged; unit
and stage evidence is a separate bound supplement. No model downloads, training,
uploads, source scan edits or production defaults changed.
