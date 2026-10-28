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
