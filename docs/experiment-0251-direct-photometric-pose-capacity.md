# Experiment0251: direct photometric pose capacity,known geometry only

Date:2026-10-20. Pre-registration before measurement.
Execution/replay:TECHNICAL_CHECK_PASSED. Complete recipe:REJECT.
Head/real-video inference:UNVERIFIED;no new reconstructed head exists.

Previous goal turn restored the actual active goal:progress in authoritative
task state,not model quality. Cleanup0250 is complete. No fitting job is live.

## Distinct mechanism and a deliberately necessary prerequisite

0241 fixed semantic attachments are not material points;0235's local patch
family and0249's direct learned geometry failed. Test **one shared rigid SE3
pose driven by raw image irradiance over a known surface**,not local endpoint
search,semantic coordinates,shape deformation or another learned checkpoint.
Eliminate nine per-view low-order SH illumination coefficients by linear
least squares at every pose. Shared pose couples all samples geometrically;
no point gets its own motion or displacement. Use existing NumPy/SciPy/Pillow.

0194 varied a lip-depth coefficient on independently generated AI views,with
unknown shape/lighting ambiguity. Here geometry is exact,fixed and **supplied**,
and only camera pose is optimized against coherent source clay. It does not
solve0194's shape ambiguity or assert that SH alone can infer identity.
This is an intentionally favorable oracle-capacity check,not video-only head
inference or a blind camera initializer. A failure stops this exact recipe
before real video;success only allows a separately registered uncertainty test
with a generic nonpatient prior. Do not pass scan geometry to real inference.

## Fixed inputs,objective and budget

Use unchanged0230 upright original720x1280 source-scan clay images and5000
surface samples,triangle IDs,barycentrics,visibility and original cameras.
Only authorizedcase001 skin bytes are opened;case002,bone,video/AI references
are not opened. Validate manifest/confirmation/source and all render hashes.
Source normals are area-weighted vertex normals,interpolated at the exact
saved barycentrics and normalized. All selected normals must be defined.

For each of five target views,-10,+10,-30,+30yaw,+10pitch,use all points visible
in front and target,inside unchanged primary original sensor ROI
x[100,620),y[500,820). Even point IDs fit;all odd point IDs validate. Require
>=200 fit and held samples and50px spans;never select by residual. Known3D
visibility/scope is **oracle assistance** and makes this more favorable than
an unknown real head,not a valid real-data mask. Store full selected IDs.

Linearize sRGB with its standard piecewise transfer and use linear luminance
weights. Sample the target at projected surface coordinates using bilinear
interpolation;do not optimize correspondences separately. At each pose solve
lighting in basis[1,nx,ny,nz,nxny,nxnz,nynz,nx^2-ny^2,3nz^2-1] on fit points
only. Nuisance lighting is unconstrained during optimization;negative final
irradiance is a rejection,not silently clamped. No per-point albedo is learned.

Initialization deliberately uses the true camera perturbed by fixed camera-frame
rotation vector[.035,-.035,.020]rad and translation[.030,-.020,.060]normalized
units. Thus this tests **local refinement only**. Focal/principal point are the
declared truth,not estimated. All views use the same perturbation,not best seeds.
q parameter scales are.02rad/.03units;bounds[-6,6],SciPy least_squares linear
loss,3-point Jacobian,max_nfev60,ftol/xtol/gtol1e-8. No regularizer,loss/seed/
SH-degree/lighting/normal/ROI/precision sweep. Full run budget120s.

Report all held point projections before/after,properR,cheirality,optimizer
termination,bounds and positive fitted irradiance. Every target must achieve
p95<=3original px;also report held photometric RMS,never substitute it for3D
camera accuracy. The exact-camera point projection oracle and least-squares
lighting algebra self-check must pass first. True pixel endpoints/cameras
must not enter the pose loss or stopping decision,only the diagnostic seed
and final evaluation. There is no reconstruction export or full-head acceptance.

On rejection:commit conclusion/recovery ref,archive only report/controls and
one actual comparison sheet,remove exclusive runner and bulky outputs before
another route. Keep originals and successful0230 benchmark unchanged.

## Research basis,not imported implementation or performance claim

[Cao et al.,CVPR2018](https://openaccess.thecvf.com/content_cvpr_2018/CameraReady/2633.pdf)
motivates geometry-proxy/light calibration in photometric face reconstruction.
Its controlled photometric assumptions are not established for this video.
Our restricted camera-only SH capacity test is independently implemented and
does not reproduce that paper or inherit its accuracy claims or code license.

## Single result,not an accepted camera or head

One run completes2.176s,exit0. No model download,training,video fit or head export.
Every original selected sample is retained. Algebra and exact projection
self-checks pass;independent OpenCV projection of frozen output agrees to
9.55e-12px maximum with proper rotations and positive held depth.

| Target | Fit/held samples | Initial p95 px | Final held p95 px | Nonpositive irradiance samples | Optimizer |
| --- | ---: | ---: | ---: | ---: | --- |
| yaw-10 |973/961|11.696|0.534|4/1934|converged|
| yaw+10 |970/978|11.781|6.140|3/1948|converged|
| yaw-30 |831/810|11.737|0.713|6/1641|converged|
| yaw+30 |854/837|11.771|0.828|6/1691|max60 evaluations|
| pitch+10 |798/845|12.054|1.292|1/1643|converged|

Four projection-only p95 values are below3px under **known exact shape,focal,
visibility and local truth-derived seeds**. This is evidence that a shared
photometric pose can use these supplied surface cues without independent local
feature matches. It is not evidence that our current real-video inference can
recover those shapes,cameras or visibility. Geometry/prior uncertainty is absent
from this favorable diagnostic and remains an unresolved next prerequisite.

The complete recipe is rejected:one geometric tail remains6.14px,one optimizer
does not terminate successfully,and all five linear SH fits predict negative
irradiance. Minima are-.329,-.386,-.252,-.658,-.006 respectively. Even though
only1-6 points/view violate positivity,they are neither discarded nor clamped
to obtain a pass. No more evaluations,seed/lighting degree change,new ROI,
exposure,normal reinterpretation or coefficient sweep is run.

Actual before/after projection panels were inspected:four rows have visibly
shorter errors;the+10 row retains a coherent offset. Gray surfaces are the
original supplied-scan clay,not generated head geometry. The displayed subset
is for legibility only;all odd IDs determine the reported held errors. No
PARTIAL_SUCCESS or video/full-head improvement claim follows.

## Closeout and cleanup before another route

Recover the exact registered runner from Git commit`3a74131`. Private compact
evidence is `assets/private/closed-experiments/0251/evidence.zip`,with manifest,
report,controls,independent replay,execution capsule and one comparison sheet.
Original scene/cameras/scan/rights hashes remain fixed. The active exclusive
runner and its raw prediction archive are removed;source can be restored from
Git and binary results regenerated from the protected0230 inputs. No full
binary backup is promised. Final archive integrity/deletion/tests are recorded
in that private closeout directory. No new package or framework needs removal.

Stop this **unconstrained-SH rigid-pose recipe**. Do not turn its partial known
geometry success into a real-video transfer or resume the older local-patch
family. Any next approach needs a distinct supported observation/physical
model and explicit unknown-shape/focal/lighting evidence,not an after-the-fact
positivity clamp or deletion of the failed target. Case002 remains unused.

Closeout verification:127 retained shared tests pass in4.624s;no new exclusive
test or package remains. Compact archive506588bytes,CRC/member SHA verified,
SHA256=`5cdf7a982f5986b77a6f928e85d91a7a81142b215395b79cc555052c429f7288`.
Seven raw files totaling742685bytes and the active208-line runner are removed;
the archive retains six evidence files,not the prediction NPZ. The pre-existing
untracked0207 document remains untouched. This is a new bounded negative result,
not completion or acceptance of the larger reconstruction objective.
