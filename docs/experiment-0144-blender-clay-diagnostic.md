# Experiment 0144: Blender clay diagnostic

Status: installation and deterministic rendering path
`TECHNICAL_CHECK_PASSED`; identity quality `UNVERIFIED`; no geometry promotion.

Blender 5.2.1 LTS was installed from the Blender Foundation package published
through the Windows package source. The installer hash was verified before
installation. Blender is GPL-3.0-or-later infrastructure; no paid model,
proprietary add-on or external reconstruction service is involved.

The new non-overwriting `tools/blender_clay.py` path imports an existing OBJ,
applies the current HeadFoundry y-down/z-back to Blender z-up/y-back conversion,
normalizes presentation scale, assigns one neutral clay material and renders
fixed front, bilateral 35-degree and bilateral 90-degree orthographic views.
It also saves a reusable `.blend` scene and a report binding the source OBJ
SHA-256, Blender version, view list and acceptance limitation.

The first real run used the wrong y-axis sign and produced an upside-down head;
that private output is preserved and excluded. The corrected run renders the
experiment-0132 mesh coherently in all five directions, and the saved scene
reopens in background mode. It does not change the source geometry.

Actual inspection makes the existing limitations clearer: the face remains
generic, the neutral lip closure is unresolved, the eye sockets lack completed
subject-specific eyes, and the nose/lip/chin relationship is not yet a strong
identity match. Therefore the render pipeline is `TECHNICAL_CHECK_PASSED`, but
the displayed identity remains `UNVERIFIED`; this is not a new reconstruction
candidate or evidence of KeenTools-level parity.

Next gate: use the fixed Blender scene only as a common human-readable review
surface. Add photo/camera overlays as a separate experiment, keeping camera
acceptance and geometry acceptance independent. No texture work is unlocked.
