# Experiment 0184: anatomical neck-section graft

Status: licensed-asset lock, fixed-camera rendering and mesh checks
`TECHNICAL_CHECK_PASSED`; neck appearance and default promotion `REJECT`.

The unchanged current head ends at one 184-edge open ring at world Y=1.2.
Its five-view renders show an abrupt short neck stump behind the jaw.
Experiment 0170's uniform extrusion was already rejected as a straight
tube. This trial instead transferred only the changing cross-sections of
the Apache-2.0 GNM Head v3.0 neutral neck, whose pinned source commit and
model hash were screened in experiment 0179. It did **not** substitute
GNM's less subject-like face.

The original 34,753 head vertices, 69,320 head faces, ears, five cameras,
hair and original head colors remained unchanged. The graft added 920
vertices and 1,840 faces over five lower rings, kept one 184-edge bottom
opening, and had minimum new triangle area 5.18e-5 model units squared.
These are topology and execution checks, not natural anatomy checks.

The five-view same-camera photo/current/candidate clay and color comparison
shows that the candidate replaces the immediate stump but creates a
posterior shoulder wedge in both profiles, a flat front lower edge and
visible overlap with the photographed collar. A crude dark-garment probe
flags 2,100 of 8,332 newly visible neck pixels at left90 and 1,041 of
8,164 at right90; that probe is only corroborative, not semantic clothing
segmentation. The visual contradiction is sufficient to `REJECT` this
graft. Do not promote a generic neck section merely because it adds
geometric completeness. Better evidence for the subject's neck/shoulder
boundary and an accepted camera are needed before another full-neck fit.

The GNM asset stayed in its existing pinned local checkout; the candidate
mesh, subject photos, reports and five-view comparisons remain ignored
local artifacts. No source image or identity derivative was uploaded.
