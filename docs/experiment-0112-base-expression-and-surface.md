# Experiment 0112: base-expression isolation and smooth surface evaluation

## Completed expression isolation

Experiment 0111 could not distinguish incompatibility on the untouched asset
from damage introduced by identity fitting. Repeat its four fixed coefficients
on the exact pinned base head, translated by the existing verified template
center, without any shape fitting. Same target, cameras and 25 cropped section
planes; only the starting geometry changes.

| Coefficient | Original base sampled crossings | Previously fitted head sampled crossings |
| --- | ---: | ---: |
| 0 | 0 | 0 |
| 0.05 | 18 | 20 |
| 0.10 | 30 | 30 |
| 0.25 | 38 | 40 |

No base trial reverses triangles, but every tested nonzero trial still has
proper lip-section crossings and unnatural enlarged profile appearance.
Therefore prior identity fitting is not necessary for this failure. This
does not prove the target corrupt, establish its intended expression semantics,
or justify another coefficient sweep. Standalone application to this base is
`REJECT` as a neutral-closure solution. These are sampled crossings, not a
complete collision test. Local report SHA-256:
`1954422efd86b4dec3cea38a90ef598652f6e3e7b695c3ceeb27afd8ad821eaa`.

## New one-variable experiment: geometric surface evaluation

The current renderer interpolates normals, but the surface remains the raw
triangulated control cage. No geometric subdivision exists in the prior code.
The [OpenSubdiv surface documentation](https://opensubdiv.org/docs/subdivision_surfaces.html)
distinguishes a control cage, finite refinement and the limiting smooth surface.
This motivates a diagnostic, not a claim that subdivision recovers identity.

Primary variable: Catmull-Clark refinement level (0, 1, 2) of the unchanged
experiment 0079 head. No mouth expression, camera, observation, texture or
identity parameter is changed. Recover only original authored quads whose
two oriented triangles are both present in the current mesh; retain the
remaining cut triangles as polygons. Do not guess diagonal merges.

Use an independent NumPy implementation of one ordinary Catmull-Clark step,
with cubic boundary smoothing and rejection of inconsistent orientation,
nonmanifold edges, disconnected vertex fans and isolated vertices. No external
application code, new checkpoint or dependency. Finite levels do not evaluate
the exact limit surface, model creases, transfer UVs, or guarantee no collisions.

Prediction: actual five-view clay and enlarged mouth crops lose control-cage
faceting. Falsification of a reconstruction improvement: generic/open lips,
profile regression or new artifacts remain. Preserve the original camera gate
and all original profile rows. New vertex/triangle counts invalidate old
triangle-ID landmark attachments; those cannot be silently reused as evidence.

Initial decision: `UNVERIFIED`; source and default remain unchanged.

## Executed smooth-surface result

Recovered 4,234 authored quads exactly from their oriented source triangle
pairs, leaving 142 neck-cut triangles. At level 0, exported geometry hashes
exactly to the source. Finite refinements then produce:

| Level | Vertices | Triangles | Left profile MAE px | Right profile MAE px |
| --- | ---: | ---: | ---: | ---: |
| 0 | 4,352 | 8,610 | 3.5891 | 7.2493 |
| 1 | 17,455 | 34,724 | 4.7725 | 7.0207 |
| 2 | 69,633 | 138,896 | 5.0324 | 6.9661 |

All output triangle areas are nonzero, but this is not an orientation/contact
certificate across different topologies. All five full-head views and mouth
crops were rendered from the actual exported geometry and inspected. Cheek
and lip faceting is reduced, while the lip opening/shelf remains and the head
is still generic. Left profile regression prevents promotion at either level.
Final visual/identity promotion: `REJECT`. The independent subdivision helper
has `TECHNICAL_CHECK_PASSED` evidence only: a known cube stencil, open-quad
boundary positions, orientation, affine invariance, repeated refinement and
malformed/nonmanifold input rejection. No default was replaced.
Full regression command `python -m unittest discover -s tests -q` passes all
92 tests; `git diff --check` passes. Neither check establishes visual acceptance.

Local `subdivision-v1` contains three OBJs, original-photo/full-head and enlarged
mouth comparisons, and report SHA-256
`aa0d67494be373e54ec8895379b2e9ad6149b045492c1fa66a55ac17e9a21f05`.
The exact experiment script identity is recorded in that report. All private
inputs and derived artifacts remain excluded from Git.

Next gate: fit and evaluate explicit visible seam/contact support on the
evaluated smooth surface, rather than fitting a triangle cage and smoothing
only afterward. Re-lift and verify all affected attachments; old triangle IDs
are invalid. Do not amplify mouthClose, add more subdivision levels in search
of identity, or count smooth appearance as likeness. Independent camera
validation and actual bilateral/frontal/oblique acceptance remain outstanding.
