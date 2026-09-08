# Experiment 0033: licensed anatomical starting mesh

Status: asset preparation `TECHNICAL_CHECK_PASSED`; subject reconstruction
`UNVERIFIED`. The output is an **unfitted generic template**, not a likeness.

The official MakeHuman base OBJ explicitly states CC0 release in September 2020.
The pinned repository's license separates graphical base/target assets (CC0)
from application logic (AGPL). Only the base OBJ and two license documents were
downloaded. No MakeHuman program logic, third-party assets or noncommercial
weights were imported. No photographs were sent anywhere.

Official evidence:
- [Pinned license](https://github.com/makehumancommunity/makehuman/blob/a8bc2d54ff0ac92e78ff71431b1023eda42bf482/LICENSE.md)
- [Core-asset reuse FAQ](https://static.makehumancommunity.org/makehuman/faq/are_makehuman_files_free.html)

`examples/makehuman-base-asset-lock.json` records revision and SHA-256 for all
three files. `tools/prepare_makehuman_head.py ASSETS OUTPUT` verifies each digest
before parsing. It selects only body-group triangles/quads above source y=5.5,
removes unused vertices, and converts y-up/face+z by the rigid rotation
diag(1,-1,-1), not a reflection. Helpers are excluded; source vertex IDs retained.
It does not import separate eyes/teeth or cap the neck crop. The crop also retains
small shoulder fragments; this needs a semantic neck boundary before production.

Local ignored artifact: `assets/private/makehuman-head-v1/template.obj`.
4,459 vertices / 8,866 triangles. Seven views in `makehuman-head-orbit-v1` were
inspected: coherent cranial, facial and ear structures are available, unlike the
previous noisy shell. Generic anatomical coherence is not evidence of subject
accuracy; the template has not been fitted to any supplied photo.

55 tests pass, including helper exclusion, quad triangulation, crop compaction,
axis conversion and empty-crop rejection. Actual pinned-asset preparation and
native rendering also completed. Next establish anatomical correspondences and
fit the template to consented photos while keeping camera uncertainty explicit.
