# Experiment 0177: continuous hair surface and photo color

Status: local Blender union and mesh topology `TECHNICAL_CHECK_PASSED`;
connected hair representation `PARTIAL_SUCCESS`; five-view appearance,
identity and default promotion `REJECT`.

The experiment-0176 v5 head, cameras and hair geometry were fixed. An initial
Blender 5.2 voxel remesh of the open cap/connector/bun yielded 211 closed
components. Keeping the largest removed 5,596 island vertices, but actual
front/side renders became porous stripes; right90 hair-mask IoU fell from
0.626 to 0.355. A closed topology alone was not a valid hair surface.

The cap was then solidified 0.08 model units toward the scalp before voxel
union at 0.02-unit resolution. After dropping four tiny islands, the local
hair component has 63,844 vertices, 127,708 triangles, one connected
component, zero boundary edges and zero edges shared by more than two faces.
The unchanged original head is a separate component. Exact-camera 512 px
renders retain approximately the prior silhouette: front/left30/left90/
right30/right90 hair-mask IoU is 0.685/0.584/0.606/0.638/0.623, versus
0.678/0.587/0.609/0.640/0.626 before union. This establishes a usable
connected *representation*, not improved likeness. The peak, rear mass and
bun still look like joined primitive forms and the ear/nape transition is
wrong in the actual images.

With geometry frozen, RGB was projected from front, left30, left90 and
right30 onto source-visible hair vertices; right90 contributed no hair
color. Only about 16,000/63,844 vertices had accepted direct observations,
so naive nearest-neighbor fill propagated a few bright samples into large
gray patches. Filtering source samples above mean RGB 80 before fill reduced
the held right90 overlapping-hair RGB L1 from 0.0656 to 0.0581. However,
on the complete photographed hair-mask area, right90 error is 0.2188 for
flat dark hair and 0.2194 for the filtered photo-color candidate: the shape
and missing coverage dominate. Left90 improves 0.1671→0.1355 under the
same full-mask metric, but it supplied training color. The right-profile
render still has a broad false crown highlight and a spherical bun.

This is not independent right-profile reconstruction validation: the prior
head, cameras, bun and connector had already used all five photos. All
subject photos, image-derived meshes, texture arrays, reports and renders
remain ignored local data and were not uploaded. The camera gate remains
open; no formal texture, mesh baseline or KeenTools-quality claim follows.

Do not optimize this appearance field further. The next candidate must
change the actual posterior/crown/bun shape and protect both pure-profile
silhouettes and the visible face/ear boundary under fixed cameras. Only a
five-view real-image review can promote it.
