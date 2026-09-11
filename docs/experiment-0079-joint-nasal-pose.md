# Experiment 0079: alternate actual-mesh pose and nasal shape

Status: `UNVERIFIED` candidate, no camera or identity acceptance/promotion.

0078's free-point camera correction misaligned the real mesh. Replace that
disconnected solve with alternating pose and nasal deformation using the
actual shared head. Reuse 0076's source-referenced displacement regularization
30, bending penalty 300, 486 editable nasal vertices, 3973 exact protected
vertices, 0.03 total movement bound and 0.5 source area-ratio floor.

Pose fitting uses the actual four reviewed canthi, eligible mouth corners
and twelve alar observations on this mesh, not unrelated freely located 3D
points. Only two oblique rotations vary: camera centers, intrinsics, frontal
and both profile cameras stay fixed. Rotation-vector components are limited
to +/-0.02rad with a 0.05rad prior and 5px observation scale. Each pose step
must not increase its penalized residual. The subsequent shape step recomputes
profile supports and must lower the combined actual-mesh point/profile
residual while satisfying the existing geometry guards. Non-nasal points
enter that acceptance diagnostic; their source vertices remain protected.

Four shape steps are retained. A fifth shape proposal exceeds the movement
bound and is rejected; the preceding accepted pose update is retained.
Both oblique z rotation-vector components reach +/-0.02rad, so this is not
an unconstrained camera optimum. Do not enlarge the bound merely to lower fit.

| Fitting diagnostic px | Source | Joint candidate |
| --- | ---: | ---: |
| Combined facial/alar/profile residual norm | 42.2049 | 32.2912 |
| Left nasal original-row MAE | 2.8416 | 2.3668 |
| Right nasal original-row MAE | 6.4675 | 4.6781 |
| Front alar mean | 8.8148 | 5.3222 |
| Left-oblique alar mean | 5.1659 | 3.7480 |
| Right-oblique alar mean | 4.8562 | 3.0050 |
| Left-oblique non-nasal mean | 3.9506 | 2.7078 |
| Right-oblique non-nasal mean | 6.6334 | 5.4777 |

Frontal non-nasal mean remains 5.1174px. This combined norm includes additional
facial observations and is not comparable to the nasal-only norm from 0076.
Compared with that bending-only candidate, joint fitting improves the oblique
facial/alar means but slightly worsens nasal contour means; no all-metric
dominance or complete visual improvement is claimed.

Maximum shape movement 0.029618 template units; minimum area ratio 0.570290;
zero reversed triangles. Exact ray-lift checks on the exported candidate and
its own cameras confirm all sixteen eligible non-nasal supports are visible
(largest gap below 3e-13). Nasal support views are separately recorded. These
checks do not establish correct anatomical correspondences or collision freedom.

Actual photo/source/candidate five-view renders use the candidate's own camera
matrices, not the old cameras by mistake. Enlarged frontal nose was inspected.
The earlier gross oblique shift is avoided, but the face remains generic and
the nose angular. This is a working coupled experimental path, not a finished
subject reconstruction or a replacement for the failed camera gate.

Next apply jointly constrained reasoning to broader face identity/proportions
instead of spending successive experiments solely on tiny nasal changes.
Retain all-view silhouette and source-shape safeguards; the unaccepted nasal
candidate is not automatically the baseline for subsequent experiments.

Private `joint-nasal-pose-v1` retains actual OBJ, cameras, iteration/pose
history, metrics and five-view comparison; its support-audit directory keeps
enlarged views. OBJ SHA256:
`b05e9e80e37d10ba0a2c7476ab3f631c6a3dd27bc097d5beb00ed45e0aab5e31`.
Camera NPZ SHA256:
`98a05bf9c94685ac749e958b5ec516546916525baf6f307415996072d5ea7612`.
Existing public suite: 78 tests pass. No private data or default promotion.
