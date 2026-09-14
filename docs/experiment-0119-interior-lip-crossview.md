# Experiment 0119: cross-view interior lip support

## Scope

Test whether adding frontal/oblique interior-lip observations prevents the
three-control closed patch from flattening. Freeze experiment 0117's cameras,
topology, boundary and retained head. Add two supports constructed from image
midpoints of detector pairs (0,13) and (17,14). Lift them onto actual visible
frontal triangles and retain barycentric support during the fit. Equal image
fractions are provisional correspondences, not physical landmark guarantees.

Use the existing profile residuals and parameter bounds. Profile and oblique
point residuals have the same 3 px scale; prior scales remain .08/.04/.04.
The frontal observations define support; obliques supply the additional fit
terms. Predict non-flat lip relief and no bilateral profile regression.

## Executed fit

The solver converges. Parameters change from
[-0.0831348,-0.0192364,-2.21e-14] to
[-0.0850030,-0.0049133,-1.69e-13]. The lower control remains effectively zero
and the upper relief decreases. Both corrected profile MAEs regress:
4.6814/5.9367 to 4.8757/5.9881 px.

Oblique upper support errors decrease from 10.8859/8.7399 to
9.2822/6.8935 px. Lower support errors remain 7.5435/4.0457 px. Exact ray-lift
checks confirm both supports remain visible in all three views (largest
world-space hit difference below 9e-16). Visibility is not correspondence
correctness. Fixed barycentric coordinates on changing depths are not exactly
fixed image coordinates; measured frontal drift stays below 0.000041 px.

The candidate fails bilateral profile protection and is `REJECT` for promotion.
Local `lip-crossview-support-v1` preserves before/after OBJ, report and actual
five-view comparison. No camera/default changes, texture or expressions.

## Distinguish depth capacity from correspondence/camera conflict

Remove the mesh and basis restrictions: independently fit each support's
positive depth along its fixed frontal ray to both oblique observations.
The converged upper point still has 8.1333/5.5117 px oblique errors, with
vertical residuals 8.1291/5.4514 px. The lower point has 7.5252/4.0643 px errors,
with vertical residuals 7.5236/3.9512 px. This is an attained free-ray solution,
not a proof of a global lower bound or independent validation.

Thus simply increasing depth freedom is not a supported cure for these
observations. Shared vertical disagreement implicates the camera/observation
combination; it does not isolate the camera as the sole cause. Do not force
these uncertain image-midpoint pairs into exact anatomical targets. Broader
reviewed facial correspondence and alignment must precede their use in a
more flexible shape model. These measurements do not establish likeness.

Actual five-view renders completed and were inspected: upper-lip relief also
weakens and the lower lip remains flat. No visual promotion is supported.
All 98 public tests and `git diff --check` pass. No public implementation changed.
