# Experiment 0101: source-visible photo seam fitting

Status: `REJECT` for promotion; frozen visible support is not retained.

Add 51 observations from the source-visible subset of the 26 central rim
candidates, matched independently to nearest points on the three photo curves
from 0100. This uses curve proximity, not equal-index cross-view correspondence.
Keep the 0098 paired offsets, source/cameras, regularization, protected region
and bounded profile iteration. Seam supports/targets stay frozen; profile-edge
support is updated. Photo hashes and source/rim provenance are checked.

Three steps are retained, fractions 0.25/0.5/0.5; the fourth has no tested step
meeting the 0.5 area floor. Final minimum area ratio is 0.501535, maximum move
0.025906 template units, zero reversed faces. Whole-profile means are
3.568295/6.524732 px versus source 3.589129/7.249347, slightly worse than the
no-seam bounded candidate's 3.539336/6.521262. One pair separation increases.

Independent ray checks on the exported mesh find only 18/14/13 of the original
20/16/15 visible samples remain visible: two lost in each view. These frozen
constraints therefore no longer all represent visible photo evidence. This
is not proof of collision, but invalidates their continued observation role.

Actual photo/source/candidate five-view renders were inspected. Generic mouth
shape and identity limitations remain. Do not promote this result or soften
the area floor. Next update visibility and nearest-curve targets between steps,
and compare on fixed reported evidence so dropping observations cannot silently
manufacture a better score. Contact constraints remain separate from visible
image constraints. Private `photo-seam-fit-v1` retains actual mesh, cameras,
history and inspected render; no personal data is committed. Public production
code unchanged; checks were actual solve, exported mesh, ray audit and rendering.
