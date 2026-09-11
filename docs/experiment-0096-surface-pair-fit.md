# Experiment 0096: relative surface-pair constraints

Status: solver `TECHNICAL_CHECK_PASSED`; real candidate `UNVERIFIED`.

Extend the existing displacement solver with optional surface_pairs: two
barycentric samples, a desired vector difference in mesh coordinates and a
positive scale. The soft equality acts independently of photo visibility.
It is not a nonpenetration inequality, collision detector or full contact model.
Existing callers without pairs retain their behavior.

Synthetic verification shrinks the gap between two separate triangles while
protecting their other vertices, preserves the pair midpoint, is invariant to
global translation and rejects invalid weights/scales. Full suite: 82 tests.

Use the thirteen actual central proximity pairs from 0095 on the unchanged
coupled head, targeting half their source vector separation at scale 300.
Keep vertices farther than 0.08 template units from all samples protected;
4173 vertices remain exactly unchanged. Neighbor and bending regularization
are 30 and 300. There are no photo observations in this isolated trial.

All thirteen gaps decrease, from source range 0.006180..0.016980 to
0.003037..0.010061 template units. Maximum movement is 0.004233; zero reversed
triangles; minimum area ratio 0.891592 against the immediate source, verified
again on the exported OBJ. These local checks do not prove collision freedom.

Actual photo/source/candidate five-view renders were inspected. Visible changes
are small and generic lip/face anatomy persists; do not promote this as a
recognizable reconstruction or complete closure. Hidden proximity constraints
were not mislabeled as visible photo landmarks. Next validate local contact
geometry and integrate separately supported visible seam observations, including
bilateral profile checks. Private `rim-pair-fit-v1` retains actual mesh, matching
cameras, gap report and five-view comparison. No personal data is committed.
