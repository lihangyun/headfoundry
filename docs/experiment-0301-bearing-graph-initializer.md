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
