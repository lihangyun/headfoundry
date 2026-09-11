# Experiment 0094: central lip-rim candidates across sections

Status: `UNVERIFIED`; no contact constraint or geometry promotion.

Apply supported sections and ordered paths at thirteen lateral positions in
a 0.30-template-unit central strip of the unchanged coupled head. Each cropped
section has two paths. Sort by mean vertical coordinate and select the upper
path's maximum y and lower path's minimum y as candidate turning locations.
Retain each candidate's triangle ID and barycentric weights. Reject ambiguous
path counts and check upper/lower vertical ordering before saving.

The 26 candidates produce paired vertical gaps from 0.002126 to 0.006423
template units. These are source-geometry measurements, not subject lip-gap
truth. The crop and vertical-extremum heuristic define provisional semantics;
they are not a complete anatomical segmentation, and corners are not covered.

Actual enlarged front/left-oblique/right-oblique clay overlays were rendered
and inspected. The curves follow the central mouth seam, but only 20/16/15 of
26 samples respectively are ray-visible. Hidden turning points may be valid
interior surface geometry but cannot automatically serve as visible photo
constraints. No points were dropped to manufacture a visibility pass.

Next distinguish the contact rim from the apparent visible seam and extend to
mouth corners. A contact constraint may involve hidden surfaces, while image
constraints need view-specific visibility. Do not require every contact sample
to remain visible or interpret ordinary contact occlusion alone as collision.
No deformation was performed. Private `lip-rim-candidates-v1` retains supported
curves, gaps, per-view ray checks and inspected overlays. Public production
code is unchanged; checks used actual thirteen-section geometry and rendering.
