# Experiment0301:global bearing initializer on unchanged short tracks

Registered2026-10-22T00:22:10Z before new implementation/scored execution.
0300closed53a620f;source581422f,result8f6a4b6. Goal active,account ordinary usage
allowed(short58%/weekly70%used). No live previous worker. Only this repo.

Evidence:0300correctly selected141pure tracks under162false pair edges,but its
held split leaves exactly TWO training observations per track. All potential
third cameras have0initial-point training observations. PnP attachment cannot
start even though seven training F edges connect five cameras. It is a structural
initializer assumption,not a signal to leak held observations or tune thresholds.

Single variable:replace two-view-point/PnP camera initialization with a globally
coupled relative-rotation and positive-bearing-scale solution. Reuse fixed owned
0300backend math only under this explicit new hypothesis;do NOT restore the
failed0300runner,model/environment or old pOSE/quadric application. Generic tested
cycle_consensus.py is shared. No new library/model,download or neural inference.
NumPy2.5.2/SciPy1.18.1/OpenCV5.0.0,CPU4threads/8GiBworking-set limit.

Unchanged:all synthetic and patient input populations,procedural0276scene/seed300,
20%pair corruption,coordinate convention,cycle selection,one SHA-min held row per
track,shared unknown-f range/seed/focal solve,training F estimation,eligible
relative-pose edges,anchor/baseline selection,all-row triangulation,BA objective/
gauge/300evaluations,independent control and all actual camera3pxgates. No frame,
point,score/mask/precision/focal/loss/budget sweep. Do not call a changed complete
pipeline a causal cycle-only improvement. Explicitly compare the ENTIRE selected
synthetic train/held arrays and clique membership with0300frozen evidence BEFORE
initialization;require array-byte identity,not ZIPtimestamp identity.

New initializer,fixed before scoring:

1. Use the same train-only E/F relative poses with>=8positive points,>=90%
   cheirality,>=1degree median parallax. Choose the same highest-support initial
   anchor/baseline pair. Traverse highest-support crossing edges to initialize
   all proper rotations;missing view-graph connection stops.
2. Average all eligible relative rotations with anchored Rodrigues least-squares,
   sqrt(training-inlier-count)weights,soft_l1scale1degree,max100evaluations,
   ftol/xtol/gtol1e-10. No held pixels or camera truth in averaging.
3. In common world coordinates,d_ij=-R_j.T@t_ji gives center direction i->j.
   Solve C_j-C_i=s_ij*d_ij for ALL eligible edges,anchor C=0and initial-edge
   scale=1. Weighted linear least-squares,rcond1e-9,require full column rank and
   EVERY finite scale>1e-9. No clamp/absolute-value/reflection rescue. Normalize
   all centers once by initial baseline length(gauge only),then t_i=-R_i*C_i.
   Record every edge/scale/residual/singular value. A tree-only control must show
   rank deficiency;graph connection alone is not metric observability.
4. Triangulate every selected track from widest training ray angle now that ALL
   cameras are initialized. No missing-point/negative-depth/error pruning to
   rescue the result. Run the unchanged shared-focal/all-train BA and score EVERY
   selected held observation with unchanged proper-matrix/positive-depth/
   non-bound reasonable-f/each-view>=6held/each-viewp95<=3pxgates.

One fixed independent control FIRST:same original141-track corrupted short-track
population/folds,>=99%purity/>=40%recall;all five proper positive cameras,true f
relative error<=2%,camera-center max/pointp95<=.01scene units,held GT-point
projectionp95<=1px,wrong+.1rad camera>3px. Original0300remainsREJECT. This run also
persists full procedural raw coordinates/edges and truth before any scored solve,
not retroactively claiming0300persisted them. Ground truth used ONLY for scoring
and seven-DOF similarity gauge,never selection/initialization/fitting.

Only after that entire control passes,ONCE read unchanged0299private raw archive
SHA256479842be79bb6f272b4792dac05d1303b9dca6ba55a8e8a36860dd5f432d6f3d,
same fixed nine native frames/cohorts/raw matches/polygons. Save all graph/status/
camera/point/training+held errors. No patient STL/scan/case002,training or upload.
No head fitting until complete camera check. A pass is provisional technical
camera consistency,NOT physical2mm/recognizable head/ACCEPT/KeenTools parity.

Implementation<=900s from registration;one worker,control<=180s,conditional actual
graph+solve<=180s,graph<=60s,whole2400s from worker start including closeout. Same
BA/focal iteration limits as0300. Stop on any failed gate/deadline,no retry. On
failure preserve tiny reports/full arrays/hash/sourceGit point,remove exclusive
0301runner/output and verify shared tests/protected hashes/independent commit
BEFORE another route. Keep successful generic graph/math and original archives,
inputs/consent/fixtures/defaults/unrelated0207. No new permission needed.

## Actual result:software control passed,actual fixed application REJECT

Executed source6480d63,one worker PID39124starts2026-10-22T00:26:56.400Z,
exits1 with a completed report in0.437s;peak working set92528640bytes,no GPU.
No main-worker retry or parameter change. Static audit confirms the complete
synthetic generator,intrinsics/projection,focal solver and BA/output blocks are
unchanged from0300. ALL selected control vertices and1128train/564held scalar
array values are byte-identical to0300;ZIPmetadata is not used as equality.

### Independent unknown-camera control:TECHNICAL_CHECK_PASSED

Same141selected tracks/100%purity/52.2222%recall with162wrong raw pair edges.
Global bearing system has rank19/19unknowns;tree-only negative has rank13/16,
so simple graph connection would not suffice. Every recovered edge scale is
positive. Five proper cameras/positive training and held depths recover without
a third initialized-point observation. BA uses6evaluations,f=1199.999999127px
(true1200,relative error7.27e-10). Independent held GT-point projection
p95=0.000000783346px;center max1.261e-10scene units,pointp95=2.613e-9scene units.
Wrong+.1rad camera gives123.646px. These tiny values concern exact noiseless
procedural geometry after putative-edge corruption,NOT real-video or skin-mm
accuracy. Full raw/procedural truth/solution/error arrays were saved this time.

### Actual source:stopped before a camera solution,not measured3Derror

Unchanged raw sparse graph:877matched vertices/1037edges,153candidate cliques,
44selected tracks(34length3,10length4),142selected observations. Source fold
counts(train,held)for0/60/120/240/300/360/420/600/690:
(7,8),(7,3),(5,3),(17,8),(12,7),(5,3),(13,0),(27,6),(5,6).
Four views lack six held rows independently of the initializer. This is selected
recipe support,not a theorem that the full video has insufficient information.

Only training pair240/600has enough common tracks for F estimation. It is a
near-repeat,not a useful stereo baseline:5/9positive points,median parallax
0.023932degree,focal initialization reaches5119.999999999992pxupper bound.
No pair meets unchanged positive/support/1degree criteria. Stop as registered:
no actual global bearing solve,BA,camera model,head or medical surface error.
Do NOT reduce angle/cheirality/support limits,extend focal bounds,leak held rows
or retry the same44tracks. All actual quality/whole-head/visual gatesUNVERIFIED.

### Preserved successful infrastructure,not failed application

Retain tools/short_track_camera.py:bounded native720x1280 unknown-focal/proper-
matrix/bearing/BA math with no private input/model paths. Retain procedural
tools/check_cycle_camera_contract.py and ONE shared regression. No blanket
physical identity or camera accuracy grant follows from this fixture. The
experiment controller/raw-patient application is retired after evidence checks.

During shared-fixture extraction,first test invocation fails only with missing
itertools import;original failure log preserved. The import is repaired and all
142shared tests then pass in5.352s,including the independent geometry replay.
No actual-patient rerun occurred. Generic extraction changes no numerical fit
code;the old private-evidence equality guard is intentionally controller-only,
not a private-file dependency of shared tests. Existing defaults stay unchanged.

Next work must change justified observation/association acquisition,not keep
changing this now-controlled camera initializer or filter by the resulting
medical/held errors. The original video still permits other preregistered source
observations;this experiment does not prove all open/self-developed routes fail.

## Verified closeout

Result/shared-backend commite10cbe9;scored source6480d63. Private
closed-experiments/0301-bearing-camera/evidence.zip is89628bytes/24members/
0images,CRCverified,SHA256
f8c997811bb4a465392d7872a2ba42a063b3e84eac908a0c1a8f31f533ae3472.
It retains full procedural raw input/truth/selected train+held/solution/errors,
bearing systems/ranks/scales,actual raw source coordinates/edges/all candidate
cliques/folds/failed initialization,byte/static/extraction audits and both the
first extraction error and repaired test log. All numerical fit ASTmatches the
retained generic backend after excluding the controller-only evidence-hash guard.

After root-contained/reparse/inventory/archive/terminal-worker checks,the
exclusive application and output directory are removed:24files/186886logical
bytes. No public weight/framework/environment exists or was reacquired. Generic
camera/graph math and procedural shared checks remain;no dangling application
import or production source/default change.142shared tests pass after cleanup
in5.475s. All15protected hashes unchanged,including original inputs/consent,
successful fixtures,unrelated0207,the two prior raw/control archives and retained
math/regressions. Original STLbytes are only hashed for integrity,not parsed or
passed to any estimator;case002content is untouched. No active model/job remains.

Source recovery is Git;compact evidence preserves these small numerical outputs,
not original full video/large historical binaries. Recreating other derived
images requires their source workflows. This closeout is within2400s;no user
action/new authority is required. Goal remains active and unachieved.
