# Experiment 0192: oracle facial correspondences, not a photo solution

Status: synthetic execution `TECHNICAL_CHECK_PASSED`; exact-correspondence
shape capacity `PARTIAL_SUCCESS`; current 1-pixel-noisy landmark estimator
`REJECT`; real-reference geometry and identity `UNVERIFIED`.

Experiments 0188–0191 only observed outer silhouette masks. This diagnostic
asks a narrower question: can the existing 82 paired, pinned CC0 MakeHuman
head controls encode the missing interior facial shape *if* front/±30°
images supplied accurate corresponding surface points? A fixed 39-point
face grid spans forehead/eyes, nose, mouth and chin and excludes neck,
shoulders and hair. Every point is an exact barycentric material match on
the generated 3D head; every camera is known. These **oracle** observations
are not available in the user's independently generated/composited photos.
Only training-view 2D projections enter a bounded 12-active-control fit;
±90° renders and true vertices are evaluated afterward. The existing
0190 identities/results were already known, so this is a capacity probe,
not an untouched method holdout. One point was removed globally when a
training-view visibility check found it occluded for one case; the final
39 points are visible in all three training views of the 12 cases.

The same fitter was run with exact 2D points and with seeded, independent
Gaussian perturbations of standard deviation 1 px per 2D coordinate at
220 × 220 resolution. This noise level is a synthetic sensitivity test,
**not** a measured error model for the subject photographs.

| Twelve-case mean | Template | Coherent silhouette fit (0190) | Exact oracle points | Oracle + 1 px noise |
| --- | ---: | ---: | ---: | ---: |
| Held left/right leading-face edge | 0.684/0.684 px | 0.469/0.469 px | 0.154/0.154 px | 0.785/0.785 px |
| True whole-mesh 3D vertex RMSE, normalized head radius | 0.01150 | 0.00747 | 0.00438 | 0.01174 |

With exact correspondence, 3D RMSE beats the template in 12/12 cases,
but the held bilateral edge is strictly better in 7/12 and the joint
edge-plus-3D comparison against the prior coherent fit succeeds in only
5/12. Under 1 px noise, only 1/12 jointly improves both held edges and
3D RMSE over the template; even the **mean** is worse than leaving the
template unchanged. All candidate meshes pass the implemented geometric
safety checks, so topology safety alone would not catch this shape error.
The selected 12-control 2D systems can be severely collinear (worst
reported condition number approximately 2.9e13). The current 0.05 ridge
weight does not yield a noise-stable estimate.

This separates two facts: the licensed control family has some capacity
under impossible-to-obtain exact material matches, but this landmark-only
inverse fit is not robust even to the stated synthetic 1 px disturbance.
The 220 px side edge is quantized, the synthetic heads/control family and
left/right views are highly correlated, and whole-mesh RMSE includes a
neck/shoulder crop. No photos, cameras, or user head were changed. It
would be incorrect to transfer the oracle coefficient fit to the subject
or to claim visual/KeenTools parity.

Next gate: derive a noise-calibrated regularizer from the known generator
prior and test it **once on disjoint synthetic identities**; this checks
whether estimator conditioning, rather than representation capacity, is
the immediate bottleneck. Any later subject trial still needs a licensed
and calibrated real correspondence source, plus enlarged bilateral
photo/old-white-mesh/candidate-white-mesh inspection. Private exact
per-case numbers, fixed point layout and runner remain under ignored
`assets/private/synthetic-head-benchmark-v1/oracle-landmarks/`.
