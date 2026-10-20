# Experiment0259: frozen recurrent tracker under actual3D motion/visibility

Date:2026-10-20. Pre-registered before new renders/inference. UNVERIFIED.
0258 passes planar precision only at0b291d0. Previous turn is progress;there
is no live prior reconstruction job. Full head/camera/scan/visual goal stays open.

## Hypothesis and immutable information boundary

The same locked TAPNext++256 recurrent model may preserve physical material
correspondences under real out-of-plane rotation and occlusion,not just planar
warps. Test a source-only **capacity oracle**,not an inferred patient head or
real-video camera. Main experimental variable is planar versus3D surface motion
in the tracker validation task;checkpoint,source,runtime,float32,8 CPU threads,
256px inference,online recurrent state and visibility logit>0 remain frozen.
No new checkpoint,framework,flow/patch refinement,resolution/precision sweep or
production change. All source/weight rights remain as0258's asset lock.

Use successful0230-upright known-motion archive SHA256
`eea2cca6a7461c594779997ba9deff785e5aabb833319dd3878513d858e79942`.
Its5000 original sampled material IDs,cameras,projections and first-hit visibility
stay immutable. Only evaluation-side source rendering may read authorizedcase001
skin;bone,case002 and original human video are not needed in this experiment.
Validate only the selectedcase001 skin asset,not the whole manifest's other
files. Patient geometry never enters the model worker or purported real-video
inference. No training/upload or medical assertion follows.

Neutral clay has no uniquely labeled surface texture;failure to track arbitrary
clay points would confound material observability with model capability. Render
one fixed object-coordinate3D noise material (scale48,detail2,roughness.5,ramp
.15-.75,emission1,Standard transform,transparent background) on the unchanged
source,using the six0230 exact cameras and720x1280 native images. This is an
idealized persistent texture,not recovered human albedo or training data. Reuse
the retained renderer/camera/scan helpers,not deleted0232 matcher code/outputs.
The old generator depends on retired wrong-axis intermediate files;do not
restore those. A minimal fresh render entry reuses exact0230 controls/arrays
without resampling or altering the successful fixture/default generator.

## Fixed sequence,input support and independent evaluator

Sequence of existing camera identities:
front,yaw+10,yaw+30,yaw+10,front,yaw-10,yaw-30,yaw-10,front,pitch+10,front.
Repeated images are exact byte/pixel repeats with continuing recurrent state,
not a query reset or a newly rendered pose. No extra intermediate frames.

Fixed input crop[0,320,720,960],native720x640,then linear resize256x256 and RGB
normalization[-1,1]. Before inference require every0230 genuinely visible point
in all six views inside this crop;otherwise stop the input precondition rather
than silently change the crop or drop offending IDs. Camera matrices and full
native pixel coordinates remain evaluator-only. Verify Blender projection replay
<=.05px and exact sample projection from unchanged source normalization.

Query **all2355 initially visible material IDs** in the front reference,with
exact2D source query seeds only. This is a conditional tracking task,not an
automatic point detector or a scan-free initializer. No texture/ROI/confidence/
error subset is selected. Points not initially visible cannot be initialized
by this test and remain explicitly outside its scope;all5000 IDs and visibility
stay in the immutable evaluator for traceability. Model input is only11 images
and2355 frame0(t,y,x) raster queries. Convert native integer-center xy through
crop offset,+.5,extent scaling and yx swap;invert exactly after prediction.
The worker receives no target tracks,visibility masks,3D points,K or extrinsics.

Every initially queried ID stays in output. For every non-query frame,score all
ground-truth-visible IDs even when the model calls them hidden. True occluded
points are assessed for visibility,not relabeled as a convenient projected
surface location. Record original ID counts/coverage,all errors and both visible
and occluded recalls;do not select only model-confident successes. Frame0 self
errors are diagnostic,not independent motion evidence.

## Gate,budget and enforced stop

All non-query frames require finite output,p95 native localization<=1px and
maximum<=3px on the entire true-visible queried population,visible recall>=.95
and,where any are occluded,occluded recall>=.95. Original camera3px,regional2mm,
complete-head and actual human visual gates are unchanged and not assessed by
this tracking test. Independent exact projection/axis/half-pixel controls and
input/output/fixture hashes must pass. No post-hoc offset,homography,axis fit,
occlusion pruning or query/region reduction may rescue a failure.

One source render process<=180s,preparation<=30s,one11-frame inference process
including strict load<=300s. Fixed CPU/memory feasibility is part of this exact
recipe;do not split/reseed queries or change precision after failure. Record
wall time from render start;total implementation/run/review after render start
<=25minutes,including a single<=5-minute two-panel review. No loop of alternative
noise scales,view density,crops,weights,thresholds or more compute.

Failure stops this exact recurrent3D recipe before real-video cameras/head
fitting. Keep compact reports,hashes,source Git recovery and at most two0259
panels;remove failed exclusive0259 runner/tests/predictions/renders and its now
exclusive model source/checkpoint/environment. Preserve successful0258 small
numeric fixture/reports and shared checks;do not present its2D success as a3D
pass. Follow cleanup0250 and commit closeout before another route.
Success is onlyTECHNICAL_CHECK_PASSED conditional3D tracking capacity,not actual
video applicability,material rigidity,cameras,2mm head or visual acceptance.
