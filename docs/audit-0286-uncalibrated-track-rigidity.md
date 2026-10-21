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

## Actual result:local checks degrade with temporal separation

Executedf00c54f,one worker7.625s including controls/input;actual pair audit6.906s.
All2701pairs are accounted:1021eligible,1666insufficient common held/training
IDs,14insufficient spatial spread. No pair was selected by its fit residual.
Of1021eligible pairs,1007yield a finite rank-two F;14model failures count as
screen failures,not omitted successes. All H estimates return a finite model.

| Predefined stratum | Eligible | Held screen passes | Failures | Median finite pairp95(px) |
| --- | ---: | ---: | ---: | ---: |
| All | 1021 | 297 | 724 | 4.243604 |
| Native frame gap12 | 73 | 72 | 1 | .951859 |
| Gap24..120 | 590 | 214 | 376 | 3.648977 |
| Gap>120 | 358 | 11 | 347 | 5.572028 |
| Non-H-dominated | 968 | 244 | 724 | 4.414082 |

These are pairwise Sampson residuals,not camera reprojection or medical mm.
The median column excludes undefined scores;the failure column includes them.
Every eligible pair's untouched held partition is scored without outlier removal.
The cohort is selected by common tracks/spread,so these counts are not an
estimate of all possible video correspondences. Longer gaps also differ in
pose/visibility/track population;this is not a controlled causal time-drift test.

Synthetic heldp95=.0000708388px;40px perpendicular displacement gives28.782018px,
while40px ALONG the epipolar line still gives.0000706051px. Thus a pass can hide
large wrong correspondences along the line. No depth/identity/rigidity certificate
follows,even for72/73adjacent passes. ExecutionTECHNICAL_CHECK_PASSED;frozen-data
screenREJECT;actual physical camera/head/medical/visual acceptanceUNVERIFIED.

Failure is not confined to0285's global camera initialization or focal upgrade:
many frozen held correspondences fail this separately fitted local image test.
This does NOT distinguish accumulated flow drift,nonrigidity,occlusion,estimator
degeneracy or other error,and does NOT prove the original video unreconstructable.
Do not rescue these tracks by residual pruning,shortening a selected cohort,
threshold changes or rerunning the retired global solver. A future observation
route needs independent physical-identity evidence and a prospective budget.

Private evidence assets/private/closed-experiments/0286-uncalibrated-tracks/
evidence.zip contains4members,262729bytes,zeroimages,SHA256
ea1fc5cbf67d817202d734da5dd85e2da623851a92a3e22ccde55a93b3ec8484.
Complete2701pair accounting/F/H matrices,controls/options,sourcefile hashes,
protected hashes and140-test output are retained;no duplicate source points,
human images or guessed geometry. Input archive remains unchanged. Source
recoveryf00c54f3891fec52380b1cc0cc41287788b7063c before exclusive runner cleanup.
All five protected hashes unchanged,including original authorized video,
successful fixture and unrelated0207.140shared tests pass in5.652s. No source
frame decode,scan/bone/case002 geometry read,new model/runtime,upload or training.

## Verified retirement

Results/recovery recorded ateb5842e before deletion. Workerpid36428terminated0;
no Python/Blender/uvjob remains. Exact resolved target/reparse/count/byte/hash
and archive checks precede removal:2raw duplicates2447679logical bytes plus
8404-byte exclusive runner,3files2456083bytes total. Source remains recoverable
atf00c54f,complete compact evidence retained;archive CRC/all four member hashes
pass after deletion. No exclusive bytecode,model,framework/environment was
created. Generic epipolar-blindspot regression remains;shared source/defaults
unchanged. Final full tests/protected checks and local cleanup commit follow
before another method;overall1200s budget retained. Goal remains unachieved.
