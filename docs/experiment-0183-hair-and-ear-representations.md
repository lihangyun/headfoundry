# Experiment 0183: posterior volume, bun locks and ear color

Status: fixed-camera five-view mesh replays `TECHNICAL_CHECK_PASSED`;
posterior silhouette and one source-view ear-color result
`PARTIAL_SUCCESS`; visual identity and default promotion `REJECT`.

The experiment-0181 head, connected hair, cameras and authorized photos
were retained. Each trial changed one component in isolation and stayed
in ignored local assets. A closed tapered posterior hair volume (3,138
vertices, 6,272 triangles) improved pure-profile hair-mask IoU under a
single nearest-neighbor 512 px mask definition: left90 0.6355→0.6526,
right90 0.6330→0.6530. It added no ear-clearance error. Its own surface
is closed, but it overlaps rather than joins the existing hair. The
five-view photo comparison shows a sharply bounded dark nape wedge, not
hair swept up behind the ears into the bun. It is `REJECT` for appearance
and production geometry.

A separate bun trial added eleven curved overlapping locks, leaving the
original head and cap untouched. The exact-mesh right90 hair IoU rose
0.6339→0.6385, while left90 fell 0.6395→0.6387 under that trial's
unchanged mask definition. Neither ear window changed. The locks are
visible in the photo comparison but form a regular striped fan around
the original ball and narrow stalk, unlike the photographed gathered
bun. This representation is also `REJECT`; more lock count is not the
missing anatomical connection.

The ear-color trial kept every vertex and camera fixed. Harmonic filling
of unobserved vertex colors erased ear folds and worsened the approximate
left ear-window RGB error. Directly sampling 724 previously unseen
vertices from right90 reduced *that source view's* ear-window RGB L1
0.0952→0.0669, but slightly worsened front and right30 skin error and
left orange/gray patches and generic ear anatomy. It is a narrow,
in-sample `PARTIAL_SUCCESS`, not cross-view identity evidence; both color
candidates are `REJECT` for promotion.

These results rule out another simple wedge, striped overlay or generic
color blur as an accepted full-head fix. No candidate was promoted or
combined. The five photos also contain no rear or rear-oblique view, so
the actual back-of-head gather remains unobserved. The cameras and masks
were developed on all five photos; none of these comparisons is an
independent reconstruction holdout. Private photos, meshes, color
candidates, reports and contact sheets were neither committed nor uploaded.
