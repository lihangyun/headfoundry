# Experiment 0202: fixed identity-fit lip-depth ablation

Date: 2026-10-13. Mesh checks `TECHNICAL_CHECK_PASSED`; actual five-view appearance
and donor/head promotion `REJECT`. Current head and cameras remain unchanged.

Experiment0201 improves source contact support but its fitted donor retains a
lower-lip bulge and inferior groove. Test whether the fitted native depth change
on the lips is sufficient to explain those defects. Preserve its coefficients,
native X/Y coordinates, source placement, cameras, image bindings, topology,
subdivision and rendering. No new fitting, weights or assets are introduced.

Restore the 203-vertex retained lip core to the repaired neutral prior's native
Z coordinates. Extend only that scalar correction to 1,429 surrounding vertices
using the existing uniform graph harmonic solve, with zero correction outside
the frozen support. The shared welded contact stays connected. This is one
diagnostic source-depth restoration, not an anatomical measurement or a generic
depth-recovery method.

The executable controls measure native XY preservation error 6.35e-18,
restored core-depth error 1.22e-17 and harmonic residual 4.56e-18. Native XY
preservation does not imply exact pinhole pixel preservation. The front mean
binding error changes 1.904→1.929 px and p95 changes 3.788→3.561 px; these are
fitting diagnostics and do not establish image likeness.

Check the cage and actual exported two-step refined mesh against both the fixed
fit and repaired neutral prior. All four comparisons have no face reversals,
maximum displacement below 0.06 and minimum area ratio above 0.5. Relative to
the fixed fit, maximum displacement is 0.010065 / 0.009397 and minimum area ratio
0.605876 / 0.721307 for cage/evaluated geometry. Protected displacement relative
to the neutral prior remains 0.019999. No threshold is rounded or relaxed.

Actual five-view Blender white meshes use the same saved camera/material/light
setup and identical native-image crops. The front and oblique lower-lip bulge
and inferior groove remain; both profiles still have the wrong lip section.
This ablation is visually `REJECT`. It cannot explain the defect solely by the
tested core-depth change. It does not rule out other depth fields, coupling with
native XY or surrounding-skin geometry, or a different representation.

Preserve the posterior-closure/corner repair from experiment0201. Before another
subject candidate, examine the continuous lip-to-philtrum/chin section and
actual visible feature support, including surrounding skin rather than assuming
the pigment border bounds the whole lip volume. Do not promote either fitted
donor or polish this rejected rollback by amplitude sweeps. A subsequent
candidate still needs recognizable front and both-side head evidence. Hair and
texture remain paused; camera acceptance and product quality are unverified.

The public regression suite passes 105 tests in the existing project environment.
The source-depth controls and all five renders are separately retained locally;
those regression tests are not visual acceptance tests. Photos, coefficients,
head meshes and renders remain excluded from Git.
