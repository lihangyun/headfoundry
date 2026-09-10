# Experiment 0051: right profile with left envelope protected

Status: `UNVERIFIED`; no accepted baseline replacement. The primary variable
is local right-profile geometry under unchanged cameras, using the existing
continuous-edge solver. It does not use uncertain dense clay landmarks.

The source is the pre-dense `neck-cut-v1` mesh. Freeze every endpoint contributing
to the left profile envelope at all 426 integer rows from 420 through 845.
Fit only the original right-profile curve, constraining each displacement to
its original frontal camera ray. Use existing regularization 100, a maximum
0.04-unit movement bound and the existing face-normal/area backtracking. No
texture, lighting, eye-helper, camera or correspondence-detector variable changes.

Actual maximum displacement is 0.0198206 template units. The measured frontal
vertex projection difference is at most 3.41e-13 pixels. Recomputed left profile
envelopes at all 426 rows differ by exactly zero, not merely at the training
curve's sparse points. Left curve MAE remains 3.64196 pixels.

Right-profile curve MAE decreases from 8.03223 to 7.12152 pixels. Some protected
locations remain unchanged, including substantial nose/lip/chin residuals.
The curve is an earlier approximate fitting input, not independent ground truth;
its reading uncertainty is larger than this small mean reduction. Do not call
this a demonstrated likeness gain or calibrated profile reconstruction.

Inspected four-view identical-shading before/after renders and a full-resolution
original-photo crop with old/new mesh-envelope overlays. Changes are modest.
The overlay still exposes a poor nose-to-upper-lip transition and angular lip
profile, despite some numeric reduction. These remaining defects prevent
acceptance. No visual smoothing or generated imagery conceals them.

Private `right-profile-protected-v1` retains actual candidate OBJ, report,
four-view comparison and photo overlay. Runners
`fit_right_profile_protected.py` and `render_right_profile_overlay.py` reuse
the existing solver/renderer. Fit input consent and source digest are checked;
all identifiable artifacts stay local and untracked. No public solver changed.
All 67 tests pass.

Next resolve the remaining nose/lip profile support and pose uncertainty before
increasing displacement. Preserve frontal and left-view evidence; a protected
constraint is not permission to hide its residual. Generic eye completion is
separate and is not mixed into this controlled geometry experiment. Camera,
identity, texture and finished-product gates remain unmet.
