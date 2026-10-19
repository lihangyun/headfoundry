# Experiment0228: independent-context rectification for precise image observations

Date:2026-10-19. Pre-registered before measurements.
Known2D screen:`TECHNICAL_CHECK_PASSED`; real transfer remains rejected in0229.

0226 demonstrates subpixel translation capability but projective patch bias;
0227 shows unconstrained affine skin patches lose coverage even with true seeds.
Test one different mechanism: estimate a coarse warp from a **separate context
population**, rectify the target image, then estimate unconstrained local2D
residuals with the existing translation tracker. This regularizes patch warp
without estimating six unstable affine parameters per point. Final endpoints
must come from pixels, not be snapped to a homography or a3D prior.

Use exactly the16 saved0226 cases. Before any truth/error evaluation, partition
by original source-feature index: index%3==0 is context, all others measurement.
Never fit the coarse warp to measured endpoints. Context homography uses fixed
USAC_MAGSAC3px/10000/0.999, seed228; require>=12 inliers,>=50% context support,
>=50px source span on both axes, finite proper orientation and finite inverse.
No context is removed using known truth. This warp is only an appearance prior,
not physical-camera or planar-face truth.

Rectify the original target grayscale into source coordinates with the estimated
homography and bilinear sampling. Transform each raw measurement seed by the
inverse warp, run0226's unchanged descriptor-seeded forward/backward LK, and map
its freely corrected endpoint back into original target pixels. Retain the
existing<=0.75px cycle,<=15 gray patch-error and image-boundary checks. The
refiner receives no known transform, truth, camera, scan or pose residuals.
Save context/measurement IDs, warp, all endpoints and eligibility, including
rejections. A unit test with a deliberately biased context warp must prove that
local endpoints correct that bias rather than copying its projections.

Evaluate only the predeclared measurement population. Each16-case result still
needs>=30 retained measurements,>=50% raw-measurement retention and p95<=1px.
Report raw and paired-cohort errors plus0226 on the same measurement IDs; changing
the population must not be disguised as improvement. One run,180s, no warp,
threshold, partition, LK or context-size sweep. Failure stops this configuration.
Only a full pass permits a separate real-video development-sentinel experiment.

Real use, if warranted, must fit context using points outside both3D pose and
validation populations. Every original camera/support gate still applies.
No images are uploaded or used to train; case002/scans/defaults remain untouched.

## Single-run result

All16 cases pass in1.079901s. Nonidentity measurement p95=0.110565-0.327258px,
with98.75%-100% retention and78-218 eligible measurements. The same measurement
population's raw descriptor p95 spans3.546830-5.079587px. All identity controls
are zero within2.4e-12px. Context/measurement source-feature IDs are disjoint;
no measured endpoint is used to fit the homography or removed by known errors.

On source612/projective's133 fixed eligible measurement IDs,0226's translation
result has p95=1.258696px versus0.176877px here. Source0/projective improves to
0.175558px while retaining all218 measurement IDs. This is a controlled2D
observation precision result on synthetic image warps, **not** improved real3D
head accuracy, physical camera calibration or validation on a new subject.
The biased-context unit test confirms final endpoints correct a deliberately
wrong warp through image evidence rather than copying its projection.

0229's real-transfer gate rejects before pose fitting. Keep this synthetic pass
as a narrow measurement capability, not a reason to waive real context support,
anatomical correspondence or camera acceptance. No production path is enabled.
