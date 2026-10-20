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

Pre-inference clarification:appearance and query population also differ from
0258,so cross-experiment error differences cannot be causally attributed to
3D motion alone. This is a conditional capacity validation under a fixed
idealized appearance,not a matched-image motion-only ablation or proof of
real-video texture applicability. No extra run or revised gate is introduced.

First Blender launch fails before image generation because Blender does not
automatically add the script's tools directory to sys.path. Its default process
exit is0 despite the Python exception;required render metadata is absent,so
this is not a technical pass. One pre-valid-run repair explicitly adds the
tools path and uses Blender's --python-exit-code1 option. Original logs remain;
no source image/model inference or parameter trial has run on that attempt.

## Actual result: REJECT,do not transfer to video/head fitting

Source recovery:`b14fa90`;first pre-valid import failure remains recorded.
The corrected source render process finishes in8.594s;preparation in.210s.
Original5000 IDs/cameras/projections/visibility and source-normalization sample
replay remain unchanged. Every truly visible original point is inside the fixed
crop,so no support is removed for image coverage. All2355 initially visible IDs
are queried;2645 not initially visible IDs remain outside this conditional task,
not claimed successfully tracked. All21258 non-query true-visible pairs are
scored,including predictions labeled hidden;2292 true-occluded pairs are retained.

One97.531s inference process finishes normally,96.378s in worker including strict
load/hash checks. No missing/unexpected keys,194202881 parameters,the exact0258
CPU float32 source/checkpoint/runtime,and7.71-8.32s per frame. No new trial,
query split,reset,checkpoint,resolution or precision adjustment occurs.

| Frame / source view | True-visible IDs | p95 px | Max px | Visible recall | Occluded recall |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0 / front,self-query only | 2355 | 1.143 | 4.592 | 1.000 | n/a |
| 1 / yaw+10 | 2163 | 20.304 | 24.341 | .944 | .198 |
| 2 / yaw+30 | 1874 | 46.223 | 56.969 | .713 | .647 |
| 3 / yaw+10 | 2163 | 14.781 | 19.364 | .795 | .911 |
| 4 / front return | 2355 | 1.719 | 3.170 | .983 | n/a |
| 5 / yaw-10 | 2151 | 24.560 | 30.529 | .901 | .613 |
| 6 / yaw-30 | 1818 | 54.589 | 65.861 | .766 | .812 |
| 7 / yaw-10 | 2151 | 22.548 | 28.465 | .853 | .956 |
| 8 / front return | 2355 | 1.660 | 2.998 | .973 | n/a |
| 9 / pitch+10 | 1873 | 28.097 | 33.611 | .971 | .774 |
| 10 / front return | 2355 | 1.315 | 2.375 | .982 | n/a |

All10 non-query frames fail the predeclared full gate,including exact front
image returns. No camera/mesh is fitted. Matrix/axis/half-pixel checks and132
unit tests (7.577s) pass;unchanged0258 stored predictions still pass their
independent2D evaluator. These checks do not override this3D correspondence
failure. Input/output/truth hashes and original-ID association are checked.

Actual fixed bilateral30deg source/residual panels were inspected in27.988s,
within the300s review budget. Vectors are actual1x,not magnification. Read-only
motion summaries show true/predicted median displacement38.443/19.501px at+30
and38.230/14.798px at-30;the model is not simply emitting no motion,but does not
preserve the declared material locations. This is observation,not a causal
diagnosis. Repeated front input images are exactly equal;no post-hoc correction
or re-inference is applied to the failed results.

Limits:ideal procedural appearance,sparse10/20deg view changes,joint2355 queries
and this256px configuration differ from natural continuous video and0258's2D
fixture. Do not claim the result proves all learned tracking,all TAPNext
configurations or reconstruction impossible. Equally,do not carry2D success
past failed3D evidence. No temporal-density/texture/query-count/crop/weight/
threshold rescue follows this registered recipe. Camera/head/real-video quality
remainUNVERIFIED;there is no PARTIAL_SUCCESS or ACCEPT and no new head result.

## Required retirement

Archive compact local reports,exact invocations,per-ID error/visibility arrays,
source/weight/license identities,original protocol and only two0259 panels.
Remove0259 exclusive source/renders/inputs/predictions,0258's now-exclusive model
inference function/active asset lock,and its downloaded source/checkpoint and
isolated environment. Keep0258's successful small2D fixture,source-only builder,
stored-output evaluator and numerical coordinate/rights regression. Their
continued availability does not imply a retained3D model integration. All raw
originals/consent,shared helpers,0230/0254 successful fixtures,production defaults
and unrelated0207 draft are protected. Verify and commit before another route.

## Verified cleanup and recovery boundary

Compact private `assets/private/closed-experiments/0259/evidence.zip` has38
members,642196bytes,only two images;CRC and every member SHA pass. Archive
SHA256=`72537f6229403db4557034b62b0765fafd47ba9da01e99a1dc7f9d6c74822ace`.
Per-ID errors/visibility,exact protocols/invocations,reports/license identities
remain local,not full failed predictions,input renders,weights or runtime.

Removed6 prevalidated private targets,21757 files,5914112770bytes logical
(5.91decimalGB,not a measured free-space claim):raw0259 run,checkpoint,downloaded
source,the dedicated environment and two old module caches. Exclusive0259 tool
and active model example lock are retired from Git;0258 model inference is
removed while its successful builder/offline evaluator/numerical test stay.
No source/default in `src/headfoundry` changes. No matching active Python/Blender
job exists before deletion. All95 protected inputs/consent/0230/0254/0258 evidence
hashes remain unchanged. New shared mathematical bytecode may regenerate during
tests;that is not retention of the retired model integration.

Gitb14fa90 recovers our source and asset records. Deleted upstream source/large
weights need pinned redownload;deleted renders/predictions require rerunning,
not extraction from the compact evidence. Do not restore automatically.0258's
older runtime/file verification records are historical;its new retired-model
record makes current absence explicit. Original external human sources remain
untouched;case002 remains unused. Full target is still unmet.

Final132 tests pass in5.531s after retirement,and stored0258 output still passes
its independent planar evaluator without any model/runtime installed. Remaining
code has no live TAPNet/Torch/TorchVision/einops imports;those packages are absent
from the shared environment. Technical closeout verification completes751.392s
after render start,within the1500s whole-phase budget;the single two-panel review
is27.988s. Detailed protected-hash checks,source001 video/skin hash replay and
phase timing are local. Cleanup completion is not goal/head completion.
