# Experiment 0136: independent MediaPipe consensus face patch

## Question

Is the experiment-0134 conflict caused only by attaching learned landmark depth
to the wrong vertices of the current generic surface? Bypass that attachment by
building a separate face patch directly on the official MediaPipe 468-vertex
canonical topology. Use the three in-domain front/oblique predictions, the
experiment-0134 consensus depth map and the experiment-0135 cameras. No current
head vertex is deformed or replaced.

The canonical OBJ is pinned to official MediaPipe revision
`20e8f2ae3365d46fa02037b54911b72e13494809`, SHA-256
`8bac80443397e113f41a8b565ea72c59390bc031d9defab289dba7bc0c54e618`,
under the repository's Apache-2.0 license. The exact model/topology lock is
`examples/mediapipe-face-asset-lock.json`.

## Result

The 468-vertex / 898-triangle open patch is valid and renders in all five
views. Front reprojection is exact by construction and is not validation.
Oblique all-point means are 9.94 and 8.75 px, with p95 22.43 and 19.29 px.
Dense profile evidence is asymmetric:

| View | Dense mean | Dense p95 |
| --- | ---: | ---: |
| Left profile | 4.649612 px | 13.786394 px |
| Right profile | 10.578327 px | 18.882357 px |

Actual renders show a coherent but coarse open face patch with more explicit
nose/lip anatomy than the closed generic head. It remains faceted, incomplete
at the face boundary and far from a full head. The severe right-profile failure
survives removal of the old surface attachment.

Asset verification, canonical topology and exact local construction are
`TECHNICAL_CHECK_PASSED`. Integration or geometry promotion is `REJECT`.
The result narrows the next gate to independent right-profile camera and
correspondence evidence; it does not justify deforming the head toward the
patch, adding texture, or claiming recognizable/KeenTools-level identity.
