# 0379: uncalibrated check on original22observations

2026-10-28 preregistration. Prior0378closed at a2f8d23; anatomy-only follow-up
077ecfb did not prove motion or matching error. No failed model restoration.

Question: is the0352/0354stop exclusively a calibrated-pose initialization issue,
or do these original observations also fail an independent uncalibrated held
image constraint? Unlike0286 (different dense74-frame cohort), this tests exact
0344original22points and0352fixed13train/9held, not refined0378coordinates.
This is a diagnostic, not a substitute reconstruction route.

Use shared headfoundry.epipolar.fundamental (normalized eight-point/rank2) and
sampson_distance unchanged. Fit exactly once per pair (0,1),(0,2),(1,2), all13
training points. No RANSAC, filters, weighting, nonlinear refinement, focal
assumption, pose, frame change, threshold sweep or new image access. Report all
13train and all9held residuals, matrices/singular values, counts and endpoint
spans; no choosing a best pair. Per-pair heldp95<=3px is a diagnostic screen,
not the camera reprojection gate. Undefined fit/distance is a failure, not omitted.

Input partition SHA d0ef30239cfed66ec573dd529ec2037976f71499ae7eed77168855b4ed33f41a.
Verify manifest/consent identities against0378archived inputs and exact archive
SHA dceeebf1d03e748eb0e96276aa7eb34a1a6a50266d897697d26aaa5ecb10f203.
No video decoding, scan, bone, case002, model, training or upload.

Controls first: known nonplanar32point scene, first23train/rest9held, exact held
p95<1e-6; 40px displacement perpendicular to target epipolar lines must fail3px,
40px along lines must still pass (exposes unavoidable blindspot). No physical
claim from along-line pass. If controls fail stop before actual inputs.

One worker<=60s/1GiB, total30minutes incl closure. Existing NumPy only; no shared
algorithm edits. Save every residual and F in a small local JSON. Preserve source
hash/recovery and protected input hashes, retire one-shot runner after verification,
run shared tests and independent cleanup commit. Failed screen does not uniquely
identify nonrigidity: wrong matches, noise, lens effects, poor conditioning and
the unrobust linear estimator remain possible. Passing does not certify point
identity, rigidity, common three-view camera, focal, metric scale or medical2mm.
No follow-on fitting automatically authorized by a low epipolar residual.

## Actual result

Source recovery8bde479. One worker0.813s/49901568B conservative peak, exit0.
Execution/controls TECHNICAL_CHECK_PASSED; frozen observation screen REJECT.

| Native frame pair | All13train Sampson p95px | All9held Sampson p95px |
| --- | ---: | ---: |
| 240/300 | 1.780245 | 4.298664 |
| 240/630 | 1.200907 | 2.154371 |
| 300/630 | 22.439483 | 8.551298 |

All3matrices and every22-point error retained, no fit/model failure omitted.
Known-scene exactp95=1.493e-13px; perpendicular40px perturbation gives28.721px;
along-line40px perturbation still gives1.635e-13px. Thus even the passing middle
pair does not certify material identity or physical accuracy.

There is a discrepancy outside the assumed-focal/recoverPose stage: this fixed
uncalibrated estimator also fails held image constraints. It does not prove no
fundamental matrix could fit the data, nor uniquely identify nonrigidity. The
large training residual in300/630 particularly warns that a linear rank2 fit
may be poorly conditioned or affected by bad correspondences; do not interpret
its8.55px as irreducible video noise. No RANSAC retry, focal sweep, point deletion
or camera/head solve follows. All camera/medical/visual accuracy staysUNVERIFIED.

The result supports requiring independent observation/conditioning evidence
before a new camera recipe; replacing the calibrated pose seed alone is not a
demonstrated fix. It does not authorize labelling lip/eye points as wrong or
claiming that only additional recording could solve the entire task.

Compact complete evidence is retained in
`assets/private/closed-experiments/0379-projective-screen`: result.json with all
matrices/residuals/source and protected hashes, worker.json and worker.log.
No generated image, weight, environment or mesh exists. The one-shot runner is
retired to Git recovery8bde479, shared epipolar math stays unchanged. Original
partition,0378archive,rights/consent,0207 and shared implementation hashes rechecked.
