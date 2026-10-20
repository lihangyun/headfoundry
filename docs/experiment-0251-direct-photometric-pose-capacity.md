# Experiment0251: direct photometric pose capacity,known geometry only

Date:2026-10-20. Pre-registration before measurement. Status:UNVERIFIED.

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
