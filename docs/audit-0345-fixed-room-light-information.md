# Audit0345:does rotation-coupled fixed-room illumination add focal information?

Registered2026-10-23T12:06:19.000Z,before fixture/Jacobian generation.
Whole2400s through closeout/independent commit,deadline2026-10-23T12:46:19.000Z.
Goalactive/account recovered;0344cleaned4efdfc2,no model worker running.
Prior quota-only turn is no development progress,not a verified live-job wait.
Ponytail:existing NumPy/OpenCV/shared analytic camera and SVD profiler only.
Reconstruction experiment discipline only,no Peek implementation/CLI/state.

## Evidence and specific distinction

[Zhang et al.,ICCV2003,sections5.1/5.3/5.4](https://grail.cs.washington.edu/projects/stshading/879_Zhang_L.pdf)
provides a fixed camera/light rotational irradiance constraint,but its projection
is orthographic and motion is initialized from sparse features then held fixed.
It does NOT prove recovery of unknown perspective intrinsics.Independent
implementation below tests that missing premise,not its claimed reproduction.
0194uses per-viewSH/shared albedo;0251source3a74131solves each viewlight separately
and its normal basis does not depend on pose. They did not test this coupling.
0332uses uniform per-view affine exposure,not normal-dependent shared room light.
No retired implementation/checkpoint/threshold/camera/head is restored.

Other researched leads are NOTcurrent entries:BMVC2005turntable self-calibration
uses dense swept-envelope initialization;TPAMI2009sparse/incomplete initializer
assumesK. Missing360-degree head coverage,unproven fixed-axis rigidity and truncated
neck silhouettes prevent claiming a ready video solution. See primary
[BMVC2005](https://i.cs.hku.hk/~kykwong/publications/hzhang_bmvc2005.pdf) and
[TPAMI2009](https://hub.hku.hk/bitstream/10722/138033/1/Content.pdf?accept=1).
MVSCPS2025needs posed/known-camera OLAT input and actual rootLICENSE is
[CCBY-NC4](https://raw.githubusercontent.com/CyberAgentAILab/MVSCPS/main/LICENSE),
not the separately bundled MIT component. No framework/model is installed.

## Frozen own physical context and one variable

One variable:include fixed-room rotational Lambertian radiometry versus the
same projection constraints alone. Independent-per-view lights are a diagnostic,
not a selected replacement. All comparisons keep the SAMEpoints/cameras/
observations/known connectivity/noise assumptions;no observation-error pruning.

NativeW720/H1280,f1200,cx359.5,cy639.5 are diagnostic generating truth only.
Two views:anchorI,secondRy18degrees witht=p-Rp,p=(0,0,3),then divide allXYZ/t
by original baseline length so baseline1is only scale gauge. Mesh12x8vertices:
xlinspace(-.45,.45,12),ylinspace(-.75,.75,8),
z=3+.12sin(3x)cos(2y)+.1x^2. Two triangles/cell,orientationtowardnegativeZ,
area-weighted vertex normals. EveryXYZis free in analysis,not restricted to
this generating height field. Connectivity is known,not optimized or a skin
attachment. Finite positive depths/native bounds/front-facing domain required.
No image rasterizer,estimated observations,pose/shape optimizer or head export.

Fixedcamera/room light L=(.18,-.12,-.30),ambient1as radiometric scale gauge.
Normals in room are R_i*n(X),not n(X)fixed in the static-head SfM frame.
I_ij=exp(g_i)*a_j*(1+L dot R_i*n_j(X))+b_i.
a_j=.3+.05sin(2x_j+3y_j),g0=0,g1=.03,b0=.01,b1=-.005.
Alltrue irradiances positive/sensorinside[0,1]. Ambient1/sourcegain0only remove
exact intensity-scale gauges;unknownalbedo/light/gain must still be profiled.
No assumed known normal/pose/geometry/lighting/reflectance enters the information
calculation as fixed. Normals and their fullXYZderivatives come from the mesh.

Unknowns:logf,cx,cy,free view1Rodrigues3+unittranslationdirection2,ALL3NXYZ,
ALLNlogalbedos,sharedL3,g1,b0,b1. AnchorI/unitbaseline only Euclidean gauges.
Zero skew/square pixels remain assumptions,not recovered complete camera model.
No geometry/light/albedo regularizer,shape model or true-parameter prior rows.
Independent-light diagnostic replaces sharedL3byL0/L1six in room coordinates,
same generated irradiance,other nuisances unchanged.Never choose after scores.

Declared independent noise scales:.5native px, .01normalized linear irradiance.
Whiten rows accordingly. This is an ideal localGaussian assumption,NOTestimated
real-video noise or achieved precision. Use unchanged column-normalized
bundle_stationarity.focal_information rcond1e-12;rank from analytic Jacobian only.
Report full raw matrices/singularvalues/ranks/profile contrast and
sigma(logf)under those fixed assumptions,not only a pass label.

## Independent controls,limits and interpretation

Reuse native_camera_jacobian for projection;append analytic principal-point
columns. Derive area-normal/normalization,rotation/albedo/light/exposure
derivatives analytically. Independently replay forward pixels withOpenCV<=1e-9px.
Check EVERYpositive-case analytic column against BOTHcentral steps1e-6and5e-7
timesmax(1,abs(parameter));per-column normdifference/max(1,analyticnorm)<=1e-6.
Never use noisy finite differences to decide a critical-motion rank.
Normal derivatives must preserve translation/scale invariance and pass an
independent finite-difference check before profile interpretation.

Keep complete negative contexts,no tuning:planar z3;R1=I/t=(1,0,0);
ambient-onlyL0;lightparallelYaxis(0,-.30,0);and deliberate frozen-head-light
model omitting R_i. All other fixed settings/pointpopulation unchanged except
the declared negative change;negative baselines are not candidate alternatives.
Projection-only baseline and negatives must have relative profiledfcontrast
<=1e-10and no added analytic focal rank. An unexpectedly positive negative
stops numerical/control interpretation,not a stronger candidate claim.

Positive screen requires independent analytic focalrank+relativecontrast>1e-6
ANDconditional sigma(logf)<=.02. This prototype information policy is NOTthe
actual3px/2mm/head gate. Record independent-light diagnostic either way;do not
claim shared light alone is causal if independent lights also add information.
If null/weak/controlfailure,stop this fixed physical recipe;no curvature/light/
noise/count/axis/view/threshold sweep. Anypositive is only local necessary
information with exact known identities and assumed radiometry;it supplies
NOimage initializer,real rigidity,actual K,metric surface or user acceptance.

One math worker<=120s/1GiB,shared suite<=120s/1GiB,4BLASthreads,existing bounded
descendant monitor. No patient/video/scan/case002read by mathematical workers;
separate housekeeping may hash the inherited protected files for integrity only.
No network/model/runtime/
dependency/training/upload/default/0207change. Keep successful pure normal
derivative helper only if independently checked. Compact all audit arrays/
controls/source/hash/worker reports(no images)then retire one-off driver/raw
duplicates after exact archive/path/protection checks and independent commit.
Failed candidate math is not promoted merely because software tests pass.
Full requested video-head/medical/visual goal remains intact and unfinished.

### Pre-execution schema clarification,2026-10-23T12:15Z

No fixture matrices or scores have been generated. Source review found that
the prescribed no-rotation t=(1,0,0) projects some complete mesh samples outside
the native sensor:after the original baseline normalization,X is about +/-.48,
Z about3.2,and u=359.5+1200*(X+1)/Z. This negative is therefore an algebraic
projection/radiometry control,not a physically imaged native-sensor fixture.
Keep its exact motion/points and every sample;do not clamp/crop or change t.
Require positive finite depth and irradiance for all contexts;native bounds and
front-facing checks remain mandatory for the positive candidate. Report bounds
for the off-sensor negative,without pretending observations were image pixels.
All negative observations are their own forward predictions,not residuals
against positive-case data. Frozen-head is a deliberately incorrect lighting
model algebraic control,not a measured physical capture.
"No added focal rank"means rank(J)-rank(J_nuisance)=0;other nuisance/shape ranks
may increase. Joint whitened sigma is named for the declared two noise scales,
not legacy unit-pixel noise. No candidate parameter,noise,threshold or budget
is changed by these pre-score consistency clarifications.
