# Experiment 0041: planar neck termination without facial deformation

Status: clipping `TECHNICAL_CHECK_PASSED`; full head likeness `UNVERIFIED`.
No accepted geometry/default replacement. The output has an intentionally open
neck boundary and is not a watertight export.

The original MakeHuman body crop retained disconnected-looking shoulder flaps
and a stair-stepped termination. Fixed-template coordinate inspection places
the shoulder widening below y approximately 1.3 in the centered y-down frame.
This experiment keeps y<=1.2 with exact triangle-plane intersections, rather
than discarding crossing triangles or deforming the head. The plane is an
explicit template-space export cut, not an estimate of the subject's anatomy.

Primary variable: lower mesh termination. Cameras, lighting, identity geometry
above the plane and source photos stay fixed. The shared-edge intersection cache
avoids duplicate cut vertices; original retained vertices remain bit-exact. No
caps, textures, generated images, smoothing or missing anatomy are invented.

Private source: `oblique-jaw-v3/candidate.obj`, SHA-256
`76fa4dd083ff0127760211820afae8af727580aa81f4effcf2eded1308f0e6f3`.
Private output: `assets/private/subject-001/neck-cut-v1/` contains candidate OBJ,
source-index mapping/report, and fixed-camera frontal/both-profile comparison.
The comparison was inspected: shoulder flaps and irregular bottom termination
are removed; face/head geometry remains visibly the same. The neck is now short
and still generic. Neither neck fit nor identity improvement is claimed.

- Input: 4,459 vertices, 8,866 triangles.
- Output: 4,352 vertices, 8,610 triangles, including 92 new plane vertices.
- 92 boundary edges, all on the plane; zero edges with more than two incident
  faces. This does not establish vertex-manifoldness or self-intersection freedom.
- Retained original coordinates are exact. Original files remain untouched.

Implementation: `headfoundry.mesh_clip.clip_below`; tests cover shared-edge
intersections, on-plane existing vertices, no-op clipping, empty-result rejection,
invalid planes and exact retained coordinates. All 62 tests pass. Private runner
`clip_neck.py` validates local photo rights and the pinned camera bundle before
rendering. No identifiable source or output enters Git or an external service.

Next: separately inspect the anatomical/normal quality of the retained face and
ear surfaces, and retain the open-neck limitation through export validation.
Do not describe a tidy cut as a completed head. Independent camera acceptance,
individual likeness, eyes/ears, texture, UV and finished exports remain unmet.
