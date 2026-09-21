# Experiment 0140: guarded local-surface depth direction

Status: diagnostic replay `TECHNICAL_CHECK_PASSED`; visual/default promotion
`REJECT`. Camera and identity acceptance remain `UNVERIFIED`.

The target is a visibly less generic nose/lip profile under the unchanged
experiment-0132 cameras. The hypothesis is that the six compact fields failed
because they lacked spatial freedom; the counter-hypothesis is that a direct
per-vertex surface solve will either violate mesh/projection protections or
collapse to an imperceptible step. Change only the central-face displacement
direction along rays from the fixed front camera. Keep topology, cameras,
observations and all prior protection groups fixed.

A direct solve over 20,362 eligible vertices and 45 constraints yields a raw
direction with 0.038917 maximum displacement. A deterministic protected scan
can retain only scale 0.007709, or 0.000300 maximum movement. It improves both
profiles from 3.623644/4.923310 px to 3.608678/4.903806 px, the selected material
means from 10.010161/10.731319 px to 9.992236/10.722323 px, and both oblique
central means from 8.895530/5.084762 px to 8.893966/5.083102 px. Minimum relative
triangle area is 0.767886 with no normal reversals. The next sampled step fails
the protection set.

Actual five-view inspection shows no meaningful visible difference. Fitting a
30-center Gaussian RBF approximation to the same raw direction reduces its
maximum displacement to 0.009949, but every nonzero scanned step regresses at
least one protected outline, central or material group; zero is selected.
Thus the technical replay is valid but supports the counter-hypothesis. The
direct local-surface direction and its smooth approximation are rejected as
identity routes. An earlier local run with mismatched target/view order is
preserved locally as invalid and excluded from all evidence.

Private outputs `profile-material-surface-v2` and
`profile-material-surface-v3` retain the locked inputs, complete scans and
inspected comparisons. No photograph or identity-derived artifact enters Git.

