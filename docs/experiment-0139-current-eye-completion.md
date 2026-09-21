# Experiment 0139: current-head eye completion

Status: asset and geometry path `TECHNICAL_CHECK_PASSED`; visual completeness
`PARTIAL_SUCCESS`; identity/default promotion `REJECT`.

The current experimental head still rendered as two empty eye sockets, a major
human-perception defect unrelated to the profile-camera question. Change one
variable only: add the two eye components already present in the pinned CC0
MakeHuman base asset. Keep every head vertex, camera and lighting value fixed.

Apply the exact experiment-0131 whole-head coefficients to the corresponding
full-base helper vertices before the established coordinate conversion. The
experiment-0132 nose/lip fields do not touch the eye region. Both components
contain 72 vertices and 140 triangles, have zero boundary and nonmanifold edges,
and remain separate closed components. A first local run exposed a coordinate
translation sign error and produced zero visible eye pixels; it is preserved as
invalid local output and not used. The corrected run verifies the original head
vertices are bit-for-bit unchanged.

Visible eye-component pixels at 400x400 are 412 front, 282 left-oblique, 56
left-profile, 298 right-oblique and 54 right-profile. The actual five-photo /
open-socket / completed-eye sheet was inspected. The black socket holes are
replaced by coherent clay eyeballs in all views, including both profiles. This
is a clear geometric-completeness improvement, but it does not change the face
or side silhouette and does not materially improve subject likeness.

The eyes remain generic: there is no subject iris, gaze, corneal surface,
eyelid-contact fit or texture. The combined OBJ is also a disconnected
multi-component inspection candidate. For those reasons the result is
`PARTIAL_SUCCESS` for rendering completeness and `REJECT` for accepted identity
or default reconstruction. Formal texture remains prohibited until the camera
gate passes.

Private output `current-eye-helper-v2` retains the combined OBJ, exact cameras,
source locks, component topology report and visual comparison. No photograph or
identity-derived artifact enters Git.
