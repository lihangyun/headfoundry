# Experiment 0007: inspect surface deformation under provisional cameras

Status: UNVERIFIED diagnostic only; camera gate remains REJECT.

The user requested visible results. This experiment adds an inspectable 3D face
patch to diagnose camera/shape inconsistency. It is not formal full-head fitting
or advancement through the failed camera gate. It cannot establish KeenTools or
MV-HRN parity and does not replace any accepted baseline.

Baseline: frontal FaceMesh predicted depth lifted into the assumed perspective
camera. Candidate: the same topology, displaced by our regularized linear
multi-view triangulation using the three available provisional cameras. Camera
matrices, observations, and boundary are fixed; only surface displacement changes.
Laplacian displacement regularization penalizes rough local deformation. Boundary
vertices remain exactly fixed, including eye/lip openings and facial perimeter.

The 468-vertex, 852-triangle face patch was exported as separate baseline and
candidate OBJ files in ignored private storage, with a six-panel shaded preview.
88 boundary vertices remained unchanged. Maximum displacement was 0.1283 in
arbitrary units, not millimeters. Render inspection shows substantial local
changes around lips and nose. This is evidence of sensitivity, not accuracy.
The forehead perimeter and chin boundary retain the single-view prior. There is
no scalp, ear, neck, eyeball, or texture implementation in this diagnostic.

Tests cover recovery of a known synthetic displacement, exact protected boundary,
identity fixed point, and rejection of points behind a camera. No surface
quality gate is relaxed. Foldover, normal consistency, and real silhouette
agreement still require validation before any production mesh export.

The next discriminating check is camera/shape consistency using independently
reviewed anatomical observations and profile contours, followed by a full-head
template and view-dependent contour fitting. The face patch is intermediate
evidence, not the project's requested final result.
