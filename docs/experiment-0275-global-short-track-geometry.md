# Experiment0275: global geometry from frozen native-video short tracks

Registered2026-10-21T06:02:12Z,before any new camera/point solve. Whole phase
2400s including implementation,installation,one solve,review and closeout.
No accepted head exists.0274 is closed/cleaned at0e6717f.

## Hypothesis and counter-evidence

0268 proves only local synthetic observability without a permanent identity.
0267's frozen native-frame DIS observations have an overlapping74-keyframe
component0..876 covering both profiles,but fail the original full-sequence
identity contract. Joint **global** rotation/position/point estimation may use
that overlap without a permanent612->1040 track or a single incremental seed.
Main variable:global geometric estimation of this frozen observation graph.
No tracker,mask,preset,frame-density,checkpoint or threshold rescue is allowed.

This differs from0219/0220/0221's incremental SIFT/LK mapper and0224/0225's
descriptor observations:use already archived native-step DIS data and the
COLMAP4.2 global SfM pipeline,with whole identities held out before geometry.
It is a new bounded test,not a controlled improvement percentage or a restored
failed integration. Counter-evidence:old camera training fits hid drift;
flow consistency is not anatomical identity;nonrigidity and weak calibration
can defeat this method too.0267 remainsREJECT;no old conclusion is changed.

## Immutable inputs and holdout

Private0267 archive SHA256
54aa2b303e4fa6f0599628f677bf359e4125dccd1df867ea70f8b9e19154c612.
Read only its observations.npz:frame,ids,xy. Freeze literal0..876/stride12
(74frames) before candidate residuals;exclude disconnected888..1040,report
their missing coverage rather than inventing a bridge. Allids divisible by5
are excluded completely from verification/calibration/mapping. Eligible held
identities have>=4 observations in the selected component (905IDs,11694rows;
minimum59 raw held observations/frame). Other identities are training only.
No source camera,scan points,medical geometry,bone,case002 or learned depth.
No original video re-extraction is needed to estimate geometry from stored2D.

For every training-frame pair sharing>=30 distinct training IDs,write exact
same-ID matches;one observation/index per identity/frame,fail on duplicates.
No descriptor fabrication. COLMAP coordinates=stored OpenCVxy+.5;shared
SIMPLE_PINHOLE720x1280,initialf1500,principal(360,640),unknown focal,zero
distortion. Use2px geometric RANSAC,seed275,CPU4threads. Run the public
view-graph calibration then global mapping once;refine focal,not principal
point;CPU only. Otherwise pinned4.2 defaults,save every effective option before
candidate execution. All pair/camera/data choices are residual-independent.

## Dependency/implementation gate

PyCOLMAP4.2.0 is geometric infrastructure,not trained weights. Primary sources:
[BSD source notice](https://github.com/colmap/colmap/blob/4.2.0/COPYING.txt),
[global pipeline source](https://github.com/colmap/colmap/blob/4.2.0/src/colmap/controllers/global_pipeline.h),
[public API](https://colmap.github.io/pycolmap/pycolmap.html#pycolmap.global_mapping).
WindowsCPython312wheel24147180bytes,SHA256
6fac64ee716335d437637d798eaafb89c76cfa06dfd53ef8384e38d09008879d.
Inspect bundled dependency notices before executing it;missing/incompatible
rights fail closed. An isolated route-only environment may reuse installed
NumPy/OpenCV through an explicit local path;main environment stays unchanged.
No upload,training,account agreement,paid asset or new learned model.

Before patient geometry,one deterministic index/pixel/projection/triangulation
control must independently replayknown3D at<1e-7px/<1e-7 scene units and reject
duplicate observations. This is implementation evidence only. Implementation
<=600s,download/install/rights<=240s,verification/calibration<=180s,one mapping
<=300s,evaluation<=120s,review<=180s. No scientific rerun after a failed result.
Ordinary pre-solve API repairs must be recorded without changing this contract.

## Untouched held evaluation and stop

Require one model with>=80% of74frames,>=200 points,both120..168 and396..444
intervals represented,proper rotations,positive fitted depths,f inside(400,4000),
trainingp95<=3px. These are viability only,not physical camera acceptance.
No choosing among candidates by held error;multiple models fail this contract.

Freeze the camera/K model. For each eligible held ID choose its first and last
registered observations as two anchors (ordinal rule,not errors),triangulate
once by unweighted DLT,score **every remaining original observation**. Report
all missing cameras,invalid/negative depth,weak ray angle and residuals without
inlier pruning;require>=30 scored held observations at every registered frame,
>=1deg anchor angle,all finite positive-depth predictions andp95<=3px globally
and separately at every registered frame. Failed IDs/missing views count as
failures,not deletion. No robust refit/BA of held points or held camera updates.
Success is at mostPARTIAL_SUCCESS geometric consistency on unverified tracked
identities;it cannot prove anatomy,mm scale/2mm surface,full head or visualACCEPT.

Failure stops before head fitting. Preserve compact private numeric evidence,
source Git ref and at most a few necessary views;remove exclusive runner,
environment,downloads,cache/database/failed point output;verify protected
originals/shared fixtures/tests and commit local closeout before another route.
Keep the unrelated0207 document and production defaults. Never label a sparse
point cloud or supplied scan rendering as the requested editable head.

## Executed result:REJECT before held geometry or head fitting

Source019f7ad registered the experiment;9abd5c8 is the final executed source.
The fixed2D data yield74 images and1382 candidate training pairs. The shared
camera calibration returns3814.87909065px (inside the registered broad range,
not independently verified). Verification/calibration takes30.704s;one global
mapping call takes8.296s and returns **zero models**. No full camera/point/head
candidate is exported,and no held-pixel or medical-surface precision is measured.

The log records1065 pose-graph edges and rejects741 relative rotations at the
unchanged10deg default,then6 more. It establishes2603 tracks for global
positioning,but iterative retriangulation/refinement has no3D points left;
bundle adjustment reports insufficient gauge points and global mapping fails.
Graph connectivity,calibration returningtrue and optimizer convergence do not
override this failure. The data/estimator combination is rejected;the log does
not uniquely distinguish bad identities,nonrigidity,calibration,weak geometry
or numerical degeneracy. Do not claim all global SfM or all video reconstruction
is impossible. No focal,mask,pair,tracking,solver or acceptance-threshold sweep.

## Engineering controls and rights qualification

Two ordinary API failures occur before any patient geometric estimate:the camera
projection control initially passes a2D normalized ray where4.2 requires a3D
camera point;the batch verification wrapper then refuses parallel RANSAC before
writing any two-view geometry (0rows). First error sources/logs are retained.
Use the correct3D API and sequential direct calls to the **same** public
two-view estimator,retaining registered4-thread RANSAC/options/matches. No
scientific estimate is rerun after a failed score. Images,keypoints and matches
tables exactly replay the pre-wrapper-failure database;camera parameters change
only in the registered calibration. Independent synthetic projection error0px,
DLT error8.909e-16 scene units and duplicate rejection pass. These do not establish
patient accuracy. Implementation completes in<600s;scientific solve has one run.

Official wheel hash/size match registration. CoreBSD is **not** the license of
every bundled DLL. The pinned vcpkg baseline127402f1 records dependency rights:
permissive licenses,CHOLMOD LGPL/Apache,SPQR GPL and GCC runtime exception,
quadmath LGPL,winpthreads MIT/BSD;empty liblzma metadata is resolved by upstream
5.8.3COPYING (0BSD),LAPACK by lapack-reference BSD metadata. Microsoft runtime
DLLs are proprietary redistributables,not open source. This authorizes only
unmodified local research use of the official distribution,with no model fee;
it is **not** approval to repackage a proprietary product or omit copyleft/
redistribution notices. No trained weights,paid asset,training or upload occurs.
Source URLs/notices and exact metadata are retained privately. Future product
distribution needs its own complete dependency/notice review,not a BSD-only label.

The unexecuted held scheme also has a protocol limitation:first/last anchors
cannot give an independent interior residual for the globally earliest/latest
views. This run fails before that code is reached,so it contributes no patient
failure score. A future protocol must prospectively provide genuine leave-one-
view-out anchors/coverage,not count fitted anchors as independent predictions
or misattribute this design defect to a model. No retrospective pass is granted.

## Closeout

Private archive:assets/private/closed-experiments/0275-global-short-track/evidence.zip,
32members,70506bytes,zeroimages,SHA256
ad63799ccdc3261717d286012923f2dde304d06469ddcd5ab78fb9b1f4550796.
CRC/every member hash reverified after deletion. Source recovery26b4aa7;
executed runner9abd5c8. It retains compact reports/options/rights/errors,not
the full database/wheel/environment. Original0267 observations remain at their
unchanged archive hash. Recovering code uses Git;the official public wheel must
be downloaded again and generated databases need rerunning,not archive recovery.

After authoritative terminal-worker and exact repository-path/reparse checks,
remove175files/172731465logical bytes from the exclusive environment,working
directory/cache/wheel/databases and runner bytecode. Remove the exclusive Python
runner from the active tree;no failed-route-only test remains. Actual free-disk
gain is not independently measured. Main environment has no PyCOLMAP import;
shared source/tests/defaults match0e6717f. Original video and four protected
authorization/shared/unrelated files hash unchanged;skin,bone andcase002 geometry
are not read. The unrelated0207 document remains untracked and untouched.

Post-removal134shared tests pass in5.862s. Evidence/checks/closeout complete
within the registered2400s;pre-final-commit elapsed748.845s. Local focused cleanup
commit follows;no push,threshold reduction,new head or acceptance claim. Goal
remains active,notcomplete. Future work needs a different evidenced hypothesis
and a valid independent evaluation design,not reuse of this failed configuration.
