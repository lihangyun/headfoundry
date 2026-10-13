# Experiment 0204: whole-head shape preparation and support screen

Date: 2026-10-13. Basis/export controls `TECHNICAL_CHECK_PASSED`; static contour
support route `REJECT` before optimization. Head likeness remains unverified.

Prepare exactly30 unconditioned head directions from the already pinned GNM
source, matching0180's dimension count. Apply the repaired posterior closure
to both the mean and every direction. Keep source eyeball variation from the
same model; no new learned assets, expressions, demographic sampling or texture.

The candidate setup combines the proper whole-head similarity from0203 with
eight stable front/oblique observations, weak frontal eyelid contours and the
lower face-oval curve. Curve topology comes from the actual installed MediaPipe
definitions. It is not an ad-hoc17-node cross-model index table. Original source
landmarks are re-embedded on actual twice-refined triangles using the tested
public helper. The proposed shape/pose bounds and prior are declared in the
private driver; no source head is changed by this preparation.

The30-direction preparation completes locally in272.03 seconds. Mean refined
surface and mean closure replay errors are zero. A separately evaluated linear
combination differs from the fitted point basis by at most3.34e-16. This verifies
the representation actually exported, not recovery of a person's shape.

Source-visible support is checked before any optimization. Only lower-eyelid
slots40/41 and46/47 remain visible in the frontal combined skin/eyeball mesh.
Of16 proposed fixed jaw slots, only6/7/9/10 are visible. The source check rejects
the driver before optimization; it produces no fitted head and no new shape
renders. A diagnostic rerun confirms the same error, without modifying outputs.

The fixed sparse source jaw points are therefore unsuitable as direct visible
frontal contour constraints in this representation. Do not lower the count or
fit projections of hidden points to compensate. The next implementation must
derive source-visible contour/support locations and verify them after motion.
This rejects the tested static bindings, not the underlying model or all head
fitting. Learned photo curves also remain uncertain appearance cues, especially
for the independently generated references.

The prepared basis, driver, failure details and source controls remain local.
No head/camera default changes or product acceptance follow from this screen.
