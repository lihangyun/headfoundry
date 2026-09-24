# Experiment 0181: smooth spatial hair deformation

Status: local bounded deformation and exact-mesh rendering
`TECHNICAL_CHECK_PASSED`; five-view silhouette `PARTIAL_SUCCESS`;
complete hairstyle, identity and default promotion `REJECT`.

The experiment-0177 connected hair mesh, 34,753-vertex head, five cameras,
head colors and photo masks were frozen. The only proposed change was hair
geometry. A first 40-control RBF displacement along noisy per-vertex mesh
normals was **rejected by mesh safety**: tiny faces reversed even after
strong damping. The controlled follow-up used one smooth radial direction
per vertex, centered near the head, with the same 40 spatial controls.
Front, left30, left90 and right30 supplied a 128 px Gaussian-alpha mask
loss; right90 supplied no optimizer loss. The resulting candidate moves
hair vertices at most 0.0954 model units, has minimum triangle-area ratio
0.867 and zero normal reversals. No head vertex or camera changed.

The splat proxy improved all five masks, but it is not the acceptance
renderer. The actual 512 px triangle mesh was therefore rerendered with
fixed flat hair and head colors:

| View | Original connected hair IoU | Smooth-field IoU |
|---|---:|---:|
| front | 0.685 | 0.717 |
| left30 | 0.584 | 0.627 |
| left90 | 0.606 | 0.640 |
| right30 | 0.638 | 0.647 |
| right90 | 0.623 | 0.634 |

All five exact-mask comparisons favor the candidate; the right90 increase
is a transfer check for this specific deformation. It is **not an
independent reconstruction holdout**: the prior mesh, head, bun and cameras
had used all five photos. The private five-row photo/old/new sheet shows
slightly better crown and side coverage but still a smooth helmet, a
spherical bun, a weak scalp-to-bun flow and broken ear/nape transitions.
Numerical mask progress cannot override that visual rejection. Do not
promote this mesh or claim complete-head likeness. More RBF controls alone
are unlikely to create strand flow or missing ear/neck anatomy; the next
candidate must change that representation and be reviewed in real images.

Photos, masks, the candidate OBJ, reports, renders and contact sheet remain
ignored local data and were not uploaded. The camera and full-head quality
gates remain open.
