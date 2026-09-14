# Experiment 0116: explicit boundary tangent collar

Initial status: `UNVERIFIED`. One primary variable: a local camera-depth
correction near the existing patch boundary. Keep the lip shape coefficients,
all cameras, patch topology, exact stitched vertices and retained head fixed.
No shape refit or extra subdivision.

## Source audit

Measure adjacent geometric triangle normals on the same 101 boundary edges,
not interpolated shading normals. Source and new triangulation differ, so this
includes discretization effects and is not a formal C1 continuity test.

| Surface | Median angle | p95 angle | Maximum | Edges above 30 degrees |
| --- | ---: | ---: | ---: | ---: |
| Original smooth head | 2.8693 | 12.2949 | 16.9195 | 0 |
| Unfitted metric patch base | 6.8653 | 19.5998 | 99.5279 | 3 |
| Fitted metric patch | 5.5000 | 19.0269 | 102.7784 | 4 |

The problem already exists before the three lip coefficients are fitted;
coefficient adjustment is not its sole cause. Local audit report SHA-256:
`e961c4a3503f44fbc6abd0719525511ec5fff142c6528dfc92bcfb3a8c355a0a`.

## Correction protocol and numerical result

For each boundary edge, use the unchanged exterior triangle plane as a local
tangent target for the patch triangle's third vertex. Combine repeated targets
with edge-length weighting. Reject unsupported, protected or excessively large
targets. Reuse the existing metric harmonic solver to extend the correction
over a 15-pixel collar. Keep the stitched boundary and deeper patch core fixed.

71 edge targets constrain 67 vertices; 30 unsupported/protected edges are
explicitly skipped. All 13,667 core vertices and the retained head are unchanged.
The maximum movement is 0.005576 template units. Boundary median/p95/max angles
become 0 / 10.3826 / 19.0269 degrees, with no boundary edge above 30 degrees.
However, 12 source-relative triangle normals reverse and the minimum area ratio
is 0.0910. These remain diagnostic flags: a normal-dot reversal is not a formal
topological inversion proof, and improved boundary angles do not prove a good
surface in the collar interior.

Whole profile means change from 5.6565 / 6.2076 to 5.6391 / 6.2226 px: the right
profile slightly regresses. These remain fitting/diagnostic rows under rejected
cameras, not independent validation. No quality guard is weakened and no
baseline is replaced on the numerical result.

Private `patch-collar-v1` retains the actual candidate OBJ and report SHA-256
`1b53e073e89acda5e51b15323b9eaef39ba587876f62bcb202d9fefdbaea14cf`.
Actual five-view and enlarged mouth comparison is required before the final
visual decision. The model remains experimental and neutral-mouth-only.

## Visual decision

Full five-view and mouth renders completed and were inspected. They retain the
flat lower lip, visible patch transition and generic identity; small boundary
changes do not establish a meaningful likeness improvement. The candidate is
`REJECT` for promotion, despite lower seam angles. The source, camera gate and
appearance default remain unchanged. No collision freedom is asserted.

The experiment also shows that correcting only boundary-adjacent planes is
insufficient: the collar interior acquires large relative triangle changes,
while the protected lip core necessarily stays flat. Stop collar-only tuning
as an identity route. Photo-consistent lip relief and broader identity evidence
remain the substantive next constraint, not another seam-angle sweep.

Verification: existing full suite passes all 98 tests and `git diff --check`
passes. No public implementation changed; the local trial reused the tested
metric interpolation, renderer and profile routines. Private candidate and
comparison images remain local and are not committed.
