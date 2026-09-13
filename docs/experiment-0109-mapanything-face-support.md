# Experiment 0109: locate stretched surfaces by image support

Status: diagnostic `TECHNICAL_CHECK_PASSED`; reconstruction remains
`UNVERIFIED` with failed camera acceptance. No surface or mask promotion.

The same pinhole-derived frontal point map from 0108 was rendered using the
original coarse ellipse, a fixed facial rectangle and a conservatively inset
eight-point skin polygon read from the original photograph. Only retained
surface support changes. Depth, cameras, edge threshold and rendering remain
fixed; no input/model inference, smoothing, fitting or texture is introduced.
All frozen camera and dense-transfer observations remain unchanged.

The rectangle still includes lower corner regions outside skin and retains
long sheets. The inset polygon, visually checked on the original photograph,
does not retain the long sheets in its five-view projections. It retains
22,763 pixels and 2,523 mesh vertices, not a full face/head. Its depth range is
2.1061–2.2134 versus 1.8378–2.8827 for the coarse region. Horizontal/vertical
adjacent-depth p95 are about 0.00210/0.00215 versus 0.01519/0.00879. These
unverified model units are not an anatomical measurement. Fine ridges and
uncertain facial shape remain visible in the retained patch.

This corrects interpretation of the earlier render: long exterior sheets are
not evidence that every internal facial depth sample is equally malformed.
They are removed here by excluding unsupported/non-skin regions, not repairing
the full head. Neither the 48.58 px camera check nor 91.93 px direct transfer
check is improved or replaced by this display selection. There is no held
validation on the retained polygon alone and no claim of improved likeness.

Private evidence: `mapanything-face-support-v1` and
`mapanything-skin-support-v1`, each with immutable report, full/interior OBJ
and inspected five-view comparison. Region coordinates, source digest and
script hash are recorded in each report. The polygon is AI-assisted visual
reading, not a calibrated or automated segmentation algorithm.
The skin-support report SHA-256 is
`33b0ef5d3148c959b5c75a2794f1f5b9b029505fca3513264bf3c52bb9b5afc4`.

Next bounded shape experiment may treat internal image depth only as an
uncertain shape prior, aligned to the existing unaccepted template/cameras.
It must not use the rejected model cameras, call this scan fusion or silently
replace the native observations. Keep changes bounded and inspect actual
bilateral profile effects and protected frontal geometry. Shared libraries
were unchanged; existing triangulation/rasterization tools were reused.
