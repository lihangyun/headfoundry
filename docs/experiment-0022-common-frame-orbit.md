# Experiment 0022: common-frame geometry inspection

Status: `UNVERIFIED`; camera remains `REJECT`. No accepted head or likeness gain.

The five observed meshes from experiment 0021 were placed in their existing
DA3 world frame, without rigid alignment, deformation, smoothing or texture.
The reusable offline command is `tools/render_surface_orbit.py OUTPUT MESH...`.
It creates an OBJ surface union, seven clay views and a looping GIF. The union
is overlapping independent sheets, **not fused geometry**. Input hashes and
the shared display transform are recorded in the output report.

Private evidence: `assets/private/subject-001/surface-orbit-v1/` (raw) and
`surface-orbit-v2/` (with `--largest-component`). All originals remain intact.
The v2 OBJ was exported after rendering using the same component function;
subsequent command runs export it automatically before display normalization.

The primary experiment variable is removal of disconnected components, keeping
the largest vertex-connected component of each view. Retained coordinates are
unchanged. This removes 1,596 vertices and 2,055 triangles; the remaining union
has 38,173 vertices and 73,932 triangles. This heuristic can discard genuine
disconnected anatomy as well as background and is not a semantic segmentation.

The display framing is recalculated from the retained bounds (radius changes
from 0.86824 to 0.28844 in arbitrary DA3 units). Consequently the two orbit sheets
are **not a fixed-scale accuracy comparison**. Rotation angles are display
orbit angles, not independently measured capture yaw.

Visual inspection of the seven v2 views shows severe sheet intersections and
steps around eyes, nose, lips, chin, ears and hair. Removing floating fragments
improves inspection framing, not anatomical reconstruction. Same-view previews
in 0021 concealed the extent of multi-view disagreement. Direct concatenation
cannot serve as the requested head. Blind smoothing/filling would conceal the
disagreement rather than establish accurate side profiles.

46 tests pass, including OBJ roundtrip, overwrite protection, invalid indices,
and exact preservation of positions by component selection. No interactive
viewer or full head acceptance is implied by the orbit animation.

Next engineering requirement: reconcile overlapping depths while preserving
source-specific evidence and side contours; evaluate the resulting shared
surface against all five photos, with unobserved regions explicitly identified.
