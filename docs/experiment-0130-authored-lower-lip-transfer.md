# Experiment 0130: authored lower-lip transfer

## Question

Can a hash-locked CC0 anatomical lower-lip target provide the missing visible
relief on the closed-mouth experiment-0128 mesh, while preserving all eye,
bilateral-profile and mesh-safety evidence?

Keep the experiment-0128 mesh and cameras fixed. Use only
`mouth-lowerlip-volume-incr.target` from the existing MakeHuman lock. Transfer
its displacement through exact original source IDs and the same one-step
Catmull-Clark construction that produced the current smooth source. No nearest
vertex mapping is permitted. The single swept variable is target strength from
zero to its authored full value of 1.0.

The closed patch has no original target IDs, so three transfer variants answer
separate falsifiable questions:

1. Harmonic extension from the exact patch-boundary displacement.
2. Visible-triangle barycentric transfer of the removed surface into the patch,
   with a zero boundary falloff.
3. The same interior transfer after twelve graph-neighbour averaging passes.

The variants are diagnostic evidence, not interchangeable candidates. All
private inputs and derived renders remain local.

## Results

The boundary-only transfer is deterministic and stable through full authored
strength. All eight oblique eye errors are numerically unchanged. Both corrected
profile means improve, but the actual displacement and visible change are small:

| Diagnostic | Experiment 0128 | Boundary transfer, strength 1.0 |
| --- | ---: | ---: |
| Corrected left profile mean | 4.505224 px | 4.448968 px |
| Corrected right profile mean | 6.139392 px | 6.132495 px |
| Maximum displacement | 0 | 0.003523 template units |
| Minimum relative triangle area | 1.000000 | 0.952597 |
| Relative normal reversals | 0 | 0 |

The exact subdivision reconstruction matches the saved level-one source within
`1e-8`; rights, revision and target hashes are checked before evaluation. This
establishes that the small effect is not a nearest-neighbour mapping error.

Restoring removed-surface interior displacement creates more amplitude but is
not shape safe. At the first rendered nonzero strength, 0.25, direct transfer
has minimum area ratio 0.179703 and four relative normal reversals; the right
profile also worsens to 6.184030 px. Twelve graph-smoothing passes do not rescue
it: the same strength has area ratio 0.172515, 60 reversals and right-profile
mean 6.214733 px. Larger strengths degrade further. These candidates are
`REJECT` without needing likeness judgment.

## Visual decision

The full five-view photo/baseline/boundary-transfer comparison and all three
mouth sweeps were inspected. The safe strength-1.0 result is visually too small
to restore the subject's lower-lip form, mouth corners, proportions or identity.
The interior variants trade continuity for amplitude and visibly remain generic
before failing geometry safeguards.

Exact asset/transfer verification is `TECHNICAL_CHECK_PASSED`. The safe
boundary candidate is `PARTIAL_SUCCESS` for protected numerical evidence and
`REJECT` for baseline promotion. The two interior candidates are `REJECT`.
Camera, geometry, texture and product acceptance remain unchanged.

Do not spend more iterations on this isolated generic lower-lip asset. The next
shape route must carry broader subject-specific identity structure and must be
evaluated jointly against all five views; local profile gains alone are not a
path to KeenTools-level likeness.
