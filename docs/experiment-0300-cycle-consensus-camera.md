# Experiment0300:cycle-certified identities and an unknown-camera witness

Registered2026-10-22T00:11:40Z before this implementation/scored work.
Previous turn is progress:0299measured real failures and closed4535db9. Goal
active;ordinary account usage allowed(short47%/weekly68%used). No live0299job.
Use only this repo. Apply ponytail full:existing NumPy2.5.2/SciPy1.18.1/
OpenCV5.0.0 and shared procedural camera-control geometry,no dependency/model.

Evidence:new raw sparse graph has12identity-conflicting connected components
and explicit forehead-to-chin associations. Taking transitive components or
two-image appearance maxima as final observations is not robust multi-view
association. A single false bridge can merge many correct identities. This does
not establish that the original source lacks information or every SfM fails.

Primary variable:construct correspondences with complete three-or-more-view
cycles,not one-shot pair matches or chained temporal flow. Read the SAME fixed
0299private archive(bytes2003208,SHA256
479842be79bb6f272b4792dac05d1303b9dca6ba55a8e8a36860dd5f432d6f3d).
No detector/matcher inference,weights/framework reinstall,new frames,masks,
points,score threshold,medical geometry or old pOSE/quadric application replay.
Archive raw matches remain putative,not already accepted physical observations.

Build an observation graph from every unique raw pair. Enumerate maximal
cliques(size>=3,at most one observation/frame automatically). For each observation,
find all containing cliques of maximum cardinality. Retain a clique ONLY if it is
the unique maximum for EVERY member. Ambiguous overlapping equal maxima are
withheld and fully reported;no arbitrary tie or reprojection-error selection.
Cap100000maximal cliques/60s,stop rather than relax or sample. Save every candidate,
selection reason,raw/selected denominator and all native coordinates. A false
coherent clique can pass this combinatorial condition;do NOT call it identity
truth. An explicit adversarial sentinel must demonstrate that limitation.

Fixed geometry backend is independently implemented calibrated incremental
initialization plus shared-focal bundle adjustment,not a causal comparative claim
that cycle selection alone improves a previously identical camera solver. Its
necessary independent witness precedes ALL actual-patient numeric construction.
Use OpenCV native-center xy/x-right/y-down/z-forward. Shared square-pixel K,
principal point359.5,639.5,unknown f seeded1280,bounds640..5120(no focal sweep).
One held observation per selected track is frozen by SHA256('300/hold/frame/key')
minimum;all remaining>=2observations train. Held coordinates never initialize,
calibrate,fit or select a camera/point. Graph identity selection uses only indices,
not image coordinates or geometric residuals. Report all selected held rows,
including outliers/missing camera or geometry;no held-error filtering.

Training pairs with>=8common tracks get one MAGSAC F estimate(1.5px,.999,
10000iterations,seed300);shared f uses one bounded log-f least-squares solve on
essential singular-value equality,100evaluations. Pair initialization candidates
must have>=8positive F-inlier points,>=90%cheirality and>=1degree median parallax;
select most positive points,then parallax,then deterministic indices. No known
pose/focal/scan in initialization. Triangulate from widest training ray angle;
attach the camera with most known training points if>=6,one EPNP-RANSAC3px/
1000iterations/.999and iterative inlier refinement. Missing pose/point stops.
No whole-sequence global-common-point requirement:short tracks can suffice.

One shared-focal BA,all training observations,soft_l1 scale1.5px,300evaluations,
sparse finite-difference Jacobian,ftol/xtol/gtol1e-8. Gauge:anchor camera fixed,
initial baseline translation norm1with two direction DOF;other poses free.
Do not fix extra identity/shape/calibration gauges or clamp an invalid solution.
No alternate initializer,iteration/focal/loss/threshold/precision sweep on failure.

Pre-source controls,one attempt:

- Two correct four-view identities plus a false bridge must recover two tracks
  without merging them. A coherent false clique must be admitted structurally
  and explicitly identified as unverified,not falsely certified physical truth.
- Shared0276procedural five-camera/270point/three-view-short-track scene(no point
  in first AND last),hidden true f1200and poses. Independently permute observation
  indices per frame;corrupt20%of each pair's target indices by cyclic permutation.
  Minimum99%selected-track material purity,40%true-point recall(expected surviving
  correct triangles .8^3=.512),then blind unknown-camera pipeline with held split.
  Truth is isolated to scoring/7DOF similarity alignment,never constructor input.
  All five proper cameras/positive depths,focal relative error<=2%,center and3D
  pointp95error<=.01scene units,held GT-point projection p95<=1px,all held views
  >=6rows. Wrong camera rotation+.1rad must exceed3px. These are software/control
  criteria,not patient millimeters. Stop BEFORE patient construction if any fails.

Only after control success,once construct actual fixed nine-frame graph/cameras.
Require all nine finite4x4world-to-camera matrices/proper R,last row[0,0,0,1],
positive training+held depths,finite points,same reasonable non-bound f,>=6held
rows EACH view,and EACH view held reprojection p95<=3px. Missing support is
incomplete/REJECT,not an invented error score. Save all held errors/depths and
training residuals separately. No source-error masks after evaluation.

Original16train/8held pair count was a0299raw-pair readiness screen,NOT a global
SfM theorem. Here the mathematical8point F/6point pose conditions and independent
global held-camera witness replace that screen,not the actual3px/2mm/mesh/ear-
neck/full-head/visual gates. No medical skin/bone/case002content is read. No head
fit before this complete camera check;even a pass is provisional technical camera
evidence,not physical surface/recognizable head/ACCEPT or KeenTools equivalence.

Implementation<=900s from registration;whole2400s from first worker,controls<=180s,
actual construction+BA<=180s,graph<=60s,worker working set<=8GiB,no GPU. Fixed
one control+conditional one actual attempt,phase watchdog,network disabled.
On failure retain tiny source/protocol/control/all-row reports+hashes/Git ref,
then remove exclusive0300runner/tests/output before next route. No model weights
exist to delete. Protect original archive,inputs/consent,0230/0293/shared math,
defaults and unrelated0207. Verify shared tests/protected hashes and commit local
closeout. No private upload,training,push or automatic old-integration restoration.

## Actual result:REJECT initializer before actual-patient construction

Executed source581422f,one worker PID45452starts2026-10-22T00:15:44.397Z,
exits1 in0.046s;peak working set88870912bytes. No timeout/retry. The fixed
corruption identity control retains141tracks,100%material purity and52.2222%
true-point recall,with162corrupted pair edges. False-bridge and coherent-false-
clique limitation sentinels pass. This is scoped graph software evidence,not
case001physical correspondence or reconstruction acceptance.

Training-only shared-focal initialization estimates1199.914873px(true1200,
relative error0.00709%),from seven F pairs. This is only an initializer,NOT the
completed unknown-camera control. Pair2/3has36positive training points and
10.5864degree median parallax. Before any BA,the next camera has0available
training3Dpoints and stops at the preregistered six-point attachment condition.

Independent audit of frozen-observations.npz confirms EVERY selected track has
exactly TWO training observations:the third was held. Thus a point triangulated
from the initial pair cannot also have a training observation in a third camera.
All remaining cameras0/1/4have exactly0initial3Dattachments. This is a structural
limitation of the chosen two-view+PnP initializer,not a noisy threshold,bad
material identity,medical error or proof that globally coupled short tracks are
unobservable. Do not consume held data/change folds or add frames to rescue it.

No complete control camera model,no final GT-pixel/point error and NO actual
patient feature archive construction,camera or head run occurred.3px/2mm/full
head/mesh/visual remainUNVERIFIED. Do not report an actual-video precision failure.

Retain only the successful generic coordinate-free graph kernel as
tools/cycle_consensus.py and one shared regression,including its explicit false-
identity limitation and ambiguity rejection. The generic cap gets a pre-use
off-by-one guard(>=100000);the scored small fixture never approached the cap.
This is not retaining the rejected camera application or changing its result.
Retire exclusive0300runner/output after compact evidence/protected-hash checks.

Next hypothesis is a globally coupled relative-pose/bearing initializer that
uses already available training F edges without requiring a third observation
of an initialized point. It must first prove unknown camera/scale recovery on
the SAME frozen short-track control and held split,not bypass the holdout or
relax camera3px. A separately registered different initializer may reuse fixed
backend math,not silently rerun0300or restore any model integration.
