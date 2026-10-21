# Audit0286: calibration-free two-view checks on frozen native-video tracks

Registered2026-10-21T13:39:09Z,before estimates. Budget1200s including code,
one audit,report/evidence/cleanup/tests/commit.0285 closed at61db1c3. No new head.
Previous goal turn is progress:fixed-input speed/equality and actual held
projection failure are measured and exclusive failed application is removed.

Question:does the frozen0267cohort fail a local two-view image constraint too,
without0285's global initialization/metric upgrade? This is read-only diagnosis,
not a new tracker,camera/head solver or a rescue of the retired recipe.
Use existing OpenCV5.0.0/NumPy and shared sampson_distance;no new asset/runtime.

Validate onlycase001video rights/hash. Read only0267observations.npz,archiveSHA
54aa2b303e4fa6f0599628f677bf359e4125dccd1df867ea70f8b9e19154c612.
Same74frames0..876stride12,59448rows,trainingid%5!=0/>=3global observations,
heldid%5==0/>=4. No scan,bone,case002,raw-frame decode,upload or training.
All2701frame pairs are listed before actual-data model estimates. Eligible pairs require
>=30common whole training IDs and>=30held IDs,each partition spanning>=50px
in both axes in each image. Eligibility depends on counts/spread only,not errors.
Ineligible pairs remain counted with reasons,not silently discarded.

Exactly one F and one H estimate per eligible pair,only training observations:
OpenCVUsacParams,MAGSAC score,uniform sampling,threshold2nativepx,confidence.999,
maxIterations10000,randomGeneratorState286,isParallelFalse;remaining current
defaults saved before fitting. CPU4threads. No focal/K,pose,3D or old candidate.
Record model matrices,all option values,training consensus fraction,p95 and
entire HELD partitionp95 without inlier/residual pruning. No refit/second seed.
Use the existing first-order Sampson distance in native pixels,NOT direct camera
reprojection or medical mm. Undefined/invalid models count as failed pairs.

Htraining inlier fraction>=.8 flags homography-dominated pairs,using the old
diagnostic boundary,not a new selector. Report all pairs plus strata(gap12,
24..120,>120),and the non-H-dominated subset. No selection of a best pair or
model initialization. Store matrices so exact held residuals can be replayed
from unchanged source observations without retaining duplicate point arrays.

Controls before actual fits:nonplanar known3Dtwo-view pixels,only whole training
IDs fit F;heldp95<.01px. Shift held points40px perpendicular to their estimated
epipolar lines:must exceed3px. Shift40px ALONG those lines:must still pass. The
latter explicitly proves the diagnostic cannot verify along-line displacement,
point depth,metric calibration or physical identity. Generic regression retains
this limitation. Three-pixel epipolar screening is a diagnostic target,not a
logical substitute for per-view3pxreprojection;noise in both images and estimator
degeneracy can affect it. Even all pairs passing would leave camera/headUNVERIFIED.

ExecutionTECHNICAL_CHECK_PASSED means controls/complete accounting only. Any
eligible held-screen failure leaves the frozen data uncertified(REJECT for this
implemented screen),not proof all tracks/video methods are impossible. Compare
no percentages against0285's different multi-view residual/cohort. No stopping
early on the first failure;run the entire predefined cohort once within180s.
Save progress/partial failure if time limit prevents completion;no more trials.

Implementation<=600s,controls<=30s,one actual audit<=180s,whole1200s. Do not tune
threshold/point/mask/frame/model after results. Preserve compact pair reports/
matrices/hashes/Git recovery,remove exclusive case-audit runner/raw duplicates
after closeout,retain only useful generic regression. Verify original hashes,
shared tests/defaults/0207 and local cleanup commit before another route. No
model/geometry fitting,push,actual acceptance or changed full3px/2mm/head goal.
