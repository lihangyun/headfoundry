# Experiment 0161: correct OBJ axes in exact-camera Blender review

Status: renderer correction `TECHNICAL_CHECK_PASSED`; prior exact-camera
Blender overlays `REJECT` as visual evidence; reconstruction quality still
`UNVERIFIED`.

The exact-camera diagnostic imported the OBJ with Blender's default 90-degree
object rotation, then rendered it against camera matrices expressed in the
OBJ's original coordinates. Its original projection check used the **already
rotated Blender vertices** as the reference, so a subpixel replay could pass
while the wrong side of the head was shown. An added clay-only render exposed
the failure: the old front view showed a smooth head with no face; a pure side
view showed the ear and underside rather than the actual profile.

The importer object transform is now reset before joining, projecting and
rendering. The diagnostic independently parses source `v` records and fails
closed if imported world vertices differ by more than 0.00005 OBJ units. On
the unchanged experiment-0132 mesh, maximum imported coordinate error is
5.96e-8. All five Blender projection p95 errors remain below 0.000083 px;
these now compare the *original source geometry* to the locked cameras. Raw
clay and photo overlays are saved separately in the private v7 output.

Corrected views show actual face anatomy, with the nose/chin foreground much
closer to the photographs than the invalid old overlays implied. The hair bun
is absent, eye anatomy remains generic, lip/ear detail and neck termination
are visibly incomplete. This does not validate the unaccepted cameras or
establish person likeness. The CPU raster profile-boundary result in experiment
0160 used unrotated OBJ vertices and is unaffected.

Impact on earlier records:

- Experiment 0145's subpixel Blender *matrix conversion* check and its broad
  cranial-mismatch interpretation are invalidated; the source-frame check and
  corrected renders here replace that visual evidence. Existing numerical
  geometry/profile gates are unaffected.
- Experiment 0153's safe 0.20-scale candidate was re-rendered with corrected
  axes. Photo/baseline/candidate mouth crops still show no confidently visible
  identity gain. Its numerical `PARTIAL_SUCCESS` and visual/default `REJECT`
  remain, now supported by valid local visual evidence.
- Experiment 0157's full-target candidate was also re-rendered correctly. It
  remains visually generic, and its untouched profile-row regressions still
  independently require `REJECT`.

No previous malformed render is deleted or silently replaced. This correction
does not promote any geometry. Future Blender comparisons must report both
source-coordinate agreement and camera projection replay before their visual
conclusions can be considered.
