# Experiment 0125: replay deformation on reconnected patch

Compare experiment 0115's original patch against 0124's reconnected patch.
Both use the same original lip coefficients, frozen cameras and original
boundary values; metric depth is recomputed for the changed connectivity.
Do not compare against 0117's slightly different fitted coefficients.

Replay exactly the three depth-field amplitudes from 0123 on both meshes:
[-0.004972917,0.001633474,0.007143935]. Recompute fields from each mesh's own
frontal projection using identical centers, radii and eligibility. No new fit.

| Deformation check | Original connectivity | Reconnected |
| --- | ---: | ---: |
| Minimum triangle area ratio | 0.233432 | 0.883653 |
| Triangles below half area | 12 | 0 |
| Relative normal-dot reversals | 4 | 0 |

This validates improved stability for this specific replay, not arbitrary
deformation or collision freedom. Both original quality thresholds remain.
Base corrected-row profile MAEs are 4.54450/6.18484 versus 4.57436/6.17689 px;
the left profile slightly regresses. Actual five-view base-surface renders
were inspected: generic identity and the flat lower lip remain. There is no
likeness acceptance or default replacement. Numerical stability is a technical
improvement, not an accepted human reconstruction.

The independent NumPy diagonal-flip routine is available explicitly as
`headfoundry.patch.improve_diagonals`; existing triangulation defaults do not
change. It copies faces, preserves vertices and boundary edges, checks finite
input, orientation and paired-edge consistency, and improves local pair
quality within a bounded pass count. It assumes an embedded input triangulation
and does not detect all geometric overlaps or promise a global optimum.
Regression tests cover winding, unchanged input, boundary, area, stable output
and malformed connectivity. All 99 public tests and `git diff --check` pass.
Running the public helper on the actual original patch reproduces every
triangle of the private connectivity trial exactly (array equality verified).

Local `patch-quality-check-v1` retains deformation diagnostics and five-view
comparison. Reconnected base OBJ SHA-256:
`fa45a8cab8bd83bf0fffe384b947e816262338a7e971e7fa9195211606752038`.
Next use improved connectivity as an explicitly experimental input when
testing actual-surface constraints; re-lift supports after topology changes.
Do not silently reuse old triangle IDs or relax eye/profile protection.
