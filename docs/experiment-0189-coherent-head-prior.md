# Experiment 0189: coherent head controls on the development split

Status: locked CC0 source and deterministic execution
`TECHNICAL_CHECK_PASSED`; coherent-control **development split**
`PARTIAL_SUCCESS` in 4/12 cases but aggregate reliability `REJECT`;
real-reference visual quality `UNVERIFIED`.

Experiment 0188 showed that moving local silhouette vertices did not
reliably recover a fixed 3D head, even when the cameras and training views
were known. This experiment changes only the shape representation and fit:
82 paired, same-topology, pinned CC0 MakeHuman controls replace local vertex
motion. The common template and synthetic identities, front/±30-degree
training masks, ±90-degree evaluation masks and oracle cameras are unchanged.
There is no hair, texture, subject photograph or paid/noncommercial model.

One linearization of template silhouette supports produces a bounded,
regularized solve over all controls; the 12 largest resulting coefficients
are then resolved and applied coherently across the whole mesh. Control
bounds are ±0.35, ridge weight 4, and unsafe steps are halved. The fitter
receives only training masks, template topology and licensed controls. It
does not receive the generating coefficients, true vertices or held ±90°
images. The held images and true vertices determine **post-fit** scores.
The data/basis digests and embedded 348-target license lock match the
project's pinned source chain. This run does not separately re-read the
raw licensed assets' headers.

| Twelve-case mean | Template | Local fit (0188) | Coherent controls |
| --- | ---: | ---: | ---: |
| Held bilateral leading-face-edge error, 220 px image | 0.6140 px | 0.5965 px | 0.4430 px |
| True 3D vertex RMSE, normalized head radius | 0.010677 | 0.010746 | 0.008490 |
| Front training-mask IoU | 0.986218 | 0.985141 | 0.991289 |

All 12 coherent meshes pass the current triangle-area, normal-reversal and
displacement guards. Nine improve true 3D error over both earlier meshes;
five improve **both** held side edges over both; eight preserve or improve
front IoU. Only four meet every criterion jointly. The per-case results are
four `PARTIAL_SUCCESS` and eight `REJECT`, so the reliability gate for the
method remains `REJECT` despite better means. The safety checks do not
detect every possible self-intersection or anatomical defect.

This is a *development split*: the same 12 indices and their 0188 outcomes
were already visible before the method and hyperparameters were chosen.
Holding ±90° out of the numerical fit is not an independent blind method
test. The heads and controls come from one synthetic family, the cameras
are exact, the 220 px contour is quantized, and whole-mesh RMSE includes
neck/shoulder regions. None of these scores measures likeness to the five
independently generated/composited local reference images or establishes
physical camera truth. Do not promote the current subject head or claim
KeenTools-level reconstruction.

The algorithm/settings were subsequently frozen and a disjoint 12-head split
was predeclared before execution. Experiment 0190 reports its failed strict
reliability gate. That result does not justify subject-head promotion. A
future head-only route must show a robust repeat before an **experimental**
subject-head trial with unchanged cameras and exact five-view clay/photo
comparison. The local runner, per-case metrics and synthetic renders remain
under ignored `assets/private/synthetic-head-benchmark-v1/`.
