# Experiment0216: consented video and skin-scan pilot intake

Date: 2026-10-19. File/rights intake: `TECHNICAL_CHECK_PASSED`.
Benchmark calibration, scan accuracy and reconstructed likeness: `UNVERIFIED`.

## Purpose and hypothesis

The user supplied two real-person videos, each paired by the user with a skin
STL (`pi`) and a bone STL (`gu`). The user explicitly confirmed rights and subject
consent for local HeadFoundry reconstruction/error validation only. Training and
upload are excluded. Original paths, identifiers, hashes, consent and all image
derivatives are recorded only under the ignored private pilot directory.

These paired inputs offer a way to measure facial geometry against supplied
surfaces. Earlier independently generated references did not supply that
evidence. Input provenance is the variable in this intake; no shape solver,
camera fit, geometry candidate or production asset changes here.

Prediction: the videos provide frontal and bilateral facial observations and
the skin scans contain the corresponding nose/lip/chin surface. Falsification
conditions for a strict benchmark include mismatched acquisition stages,
unreliable local scan geometry or failure to obtain usable camera alignment.

## Executed checks

| Local case | Video | Skin triangles | Largest skin component area |
| --- | --- | --- | --- |
| real-case-001 | 720x1280, nominal34.77s | 280740 | 99.9943% |
| real-case-002 | 720x1280, nominal20.30s | 278776 | 99.9843% |

All four STLs pass strict binary byte/count/finite-position parsing. After
exact-coordinate welding, all have zero degenerate triangles, boundary edges,
nonmanifold edges and inconsistent two-face edge directions under the implemented
checks. This is not a scan-accuracy, anatomy or self-intersection certificate.
Small disconnected components are retained and measured, not removed. STL units
remain unverified because the file format does not encode them here.

Sixteen frames per video were decoded at checked frame indices, hashed and placed
in contact sheets. Durations and sample times use reported frame count/fps;
container presentation timestamps and every intervening frame are not verified.
Actual reviewed samples show front, bilateral yaw and pitch motion. The review
does not establish a complete360-degree camera orbit or unseen posterior capture.
Whole-frame sharpness is descriptive and does not pass a face-region blur gate.

Blender5.2.1 rendered24 source-only images: two cases, two scan types, six raw
axis views. Each case uses one uniform display transformation for skin/bone;
original coordinates and files remain intact. Three skin views are rotated for
upright intake sheets beside selected video frames. These sheets have different
poses/projection/crops and are **not aligned reconstruction comparisons**.

## Actual source review

Both skin scans visibly cover the face, nose, lips, chin and cranial exterior.
Their eyes appear closed while the reviewed video eyes are generally open.
Posterior/ear regions show irregular scan surfaces and the neck has an artificial
cut/cap. Do not treat these regions as uniformly accurate target anatomy.
Appearance suggests useful facial surfaces but does not verify source acquisition
dates, units, segmentation precision or expression equivalence. Bone geometry is
an auxiliary reference, not a substitute for external facial-surface truth.

## Next bounded development gate

1. Use case001 for development. Reserve case002 from shape/camera tuning until
   the method and thresholds are fixed. Intake previews were viewed for both,
   so do not describe the second subject as an untouched blinded test set.
2. Record units and capture/scan stage correspondence when supplied. Unknown
   scale permits normalized diagnostics, not claims in millimeters.
3. Build a frame/camera baseline with explicit face-region observations and
   withheld video frames. The stationary room background must not define the
   moving head's coordinate frame. Source scans used for registration/calibration
   must be disclosed; such a diagnostic cannot certify photo-only recovery.
4. Before geometry fitting, inspect scan-to-video nose/cheek/chin projection in
   front and both profiles. Record pose/expression uncertainty and scan defects.
5. Then run one predeclared geometry candidate with the same frame split and
   alignment convention. Require full white-mesh/profile evidence, regional
   surface errors and protected-region checks. Reject numeric-only improvements
   that introduce visible defects. No parameter sweep of the frozen0214/0215
   neck setup is justified by this new data.

Two subjects are a development pilot, not the original population benchmark or
evidence of KeenTools parity. Goal completion and geometry acceptance remain
unproven.

## Reproduction and local artifacts

Use the existing project Python environment plus installed OpenCV/Pillow/SciPy.
No dependency, model or training asset was downloaded.

```text
python tools/intake_real_capture.py <user-local-source-directory> assets/private/real-capture-pilot-v1 --consent-record <confirmed-chat-record> --consent-date 2026-10-19
blender --background --python tools/render_real_scan_intake.py -- assets/private/real-capture-pilot-v1
python tools/review_real_capture.py assets/private/real-capture-pilot-v1
python -m unittest discover -s tests
```

All outputs refuse overwrite. Preserve the first run and choose a new private
directory for a deliberate replay. `manifest.json` binds all six source files;
`report.json` records scan/video checks; `scan-preview/report.json` binds renders;
`input-review/report.json` records exact frame/view/display-rotation layout.
Private consent and inputs validate both before and after intake. Raw videos,
STLs, local paths, source names, frames and renders are excluded from Git.

Validation: all133 public tests pass, including exact STL reconstruction and
corrupt/truncated/nonfinite input rejection. Both actual intake/preview/review
jobs completed successfully. Current outcome is a usable source-inspection
foundation; no reconstructed person head has yet passed.

### User metadata confirmation after intake

On2026-10-19 the user confirmed millimeter STL units and matching video/scan
acquisition stage for both cases, without intervening face-shape-changing events.
The private `provenance-confirmation.json` binds this statement to the untouched
original manifest. Independent scan accuracy and expression equivalence remain
unverified. See0217 for the subsequent rejected camera-association screen.
