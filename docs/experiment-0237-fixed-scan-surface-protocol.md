# Experiment0237: freeze the source-surface evaluation, not another head fit

Date:2026-10-19. Pre-registered before implementation or region-preview generation.
Status:`TECHNICAL_CHECK_PASSED` for metric QA and coarse source-region review;
complete head/scan accuracy remains`UNVERIFIED`. This does not reconstruct a head.

The real pilot still lacks fixed source-region and global-alignment records.
Earlier surface-registration scores use sampled nearest points, not an exact
point-to-triangle query. Those numbers must not silently populate the2mm surface
gate. Close this prerequisite while keeping0235/36's stop decisions intact.

Use only case001 original skin source, existing rights/unit/stage confirmation
and original face order. A private source-only proposal defines coarse nose,
perioral, chin, bilateral cheek, forehead and remaining frontal-face regions.
Freeze the proposal before rendered review or any candidate errors. It uses
explicit source-coordinate windows and closed-eye exclusions, not nearest
candidate matches. Mark a triangle exterior only if its centroid has an exact
first-hit view from front or either45degree oblique with.01mm visibility gap.
This centroid rule is a declared coarse scope, not proof of every point's
visibility or medical/anatomical segmentation accuracy. Unscoped scalp/back,
eyelids, artificial neck cuts and enclosed surfaces remain separately reported;
they are not declared successfully reconstructed or dispensable to the goal.

Render front, both45degrees, both90degrees and back with region colors. Reject
the proposal if boundaries visibly miss the named anatomy or include clear
source defects; do not tune it against any candidate/error map. Freeze reviewed
original triangle IDs and2048 area-uniform samples per region with seed237 plus
region index. Also retain5000 full-source samples, unchanged seed230, so region
scores cannot stand in for complete-head coverage. Record all areas/counts,
source/sampling/proposal hashes, exclusions and actual reviewed images.

Use installed Blender BVH closest-triangle queries with epsilon0 in original
millimeters, translated by one common fixed source center for numerical accuracy.
No new dependency or approximate nearest-vertex substitution. Require an
analytic coarse-triangle distance fixture (2mm above triangle interior, far
from every vertex) and exact source-self replay max<=.001mm. Source self replay
is only metric QA, never a video-derived candidate. One180s reference run.

For later candidate scoring, require a hash-bound finite triangular geometry
archive and one explicit positive uniform4x4 candidate-to-scan similarity,
applied once to the entire output. Reject reflection, anisotropic scale, invalid
homogeneous row, missing units, or changed source/regions. No ICP, per-region
alignment, distance trimming or error-based exclusion. Report source-to-candidate
distances for the full source and every frozen region, and candidate-to-full-scan
distances for all area-uniform candidate samples, including closest source face
IDs/region membership. Save every sample/distance,2mm coverage, median,p95,max;
do not hide extras or unsupported candidate area behind a directional average.

The initial face-region review can establish an engineering diagnostic scope,
not scan acquisition accuracy or independently quantified semantic-boundary
uncertainty. Keep those `UNVERIFIED`; do not write the diagnostic's partial-face
p95 into the complete-product acceptance manifest or claim2mm physical accuracy.
Full-head/scalp/ear/neck, video-only inference, profile and user visual gates stay
required. Case002, originals, defaults and failed models remain untouched; no
training/upload or source-scan substitution. A failed proposal or metric check
stops this configuration before any candidate measurement.

## Executed result and remaining limits

The first generator stops at a mismatched existing preview-replay function
signature after saving the region archive and first image. Preserve that failed
directory and exact producer. One interface-only repair uses a separate output
directory; every archived array is bit-identical to the failed first attempt.
No region/coordinate/visibility/sampling/threshold change is made. The successful
reference run completes in8.79s, with all six source-region views inspected.

Seven coarse face groups contain2048 samples each, plus5000 area-uniform
full-source samples:19336 total. Independent original-triangle/barycentric replay
has exactly0mm error, and all regional sample memberships match the frozen face
IDs. The reviewed face scope covers20.3053% of source area, **not the whole head**.
The rest remains represented in the full-source sample group and separately
unverified; scalp/ears/neck/posterior accuracy has not become optional.

Blender5.2.1LTS/NumPy2.3.4 BVH self replay gives p95=0.000007864mm and
max=0.000361914mm. These are numeric self-consistency, not scanner accuracy.
Analytic integration fixtures return exactly2mm above a coarse triangle interior,
preserve reversed original polygon IDs, and measure2mm in both directions after
one declared similarity. An omitted distant triangle retains a223.75mm error
and50%2mm coverage, proving that reverse-only proximity cannot hide missing area.
All177 regression tests pass, including complete entrypoint provenance/transform
and refusal paths. No real reconstructed candidate has yet been measured.

The final measurement entrypoint additionally binds source-only review bytes,
exact case001 skin/video identity, a declared scan-free inference provenance,
sampler and actual Blender/NumPy versions. A source-code audit proves all four
numeric helpers unchanged after those entrypoint-only guards. Changed units,
source, review, runtime, sampling or measurement code fails closed. Source and
semantic-boundary uncertainty remain explicitly unquantified/`UNVERIFIED`.

Reproduction:run `tools/freeze_scan_reference_0237.py` through local Blender only
in a new authorized experiment (the frozen output intentionally refuses reuse).
The existing private reference/region archive and source-only review are ready
for later measurement. `tools/scan_surface_metric_0237.py` accepts, after Blender's
`--`, the private reference directory, a hash-bound candidate record and a new
private output directory. The candidate supplies finite `vertices`/`faces` NPZ,
one4x4 positive similarity and explicit video-only provenance; no ICP is run.
Its partial-region results must not be copied into a complete-product acceptance
manifest. Existing surface/model/image gates and actual user review still apply.
