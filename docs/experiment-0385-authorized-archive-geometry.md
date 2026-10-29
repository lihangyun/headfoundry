# 0385: authorized archive-only geometry exception

2026-10-29 user explicitly approved the 0384 proposal ("允许，继续任务").
Goal verified active; account usage available. Start14:08:35UTC, deadline
14:28:35UTC (22:28:35 Asia/Shanghai), including closure. No neural call,
download, new frame, scan, case002, training or production-default change.

Single variable: replace0383operational48/36/20%-hold entry with exactly37
existing admitted tracks,28train/9held. This is an authorized exception after
seeing count, NOT a new matcher or retrospective reversal of0383REJECT.
Archive SHA75559d3b50277fddc66b6a50f179d1bb4633e885976fb905dee864c060b62266;
raw member SHAc9d28a59acbd23eefb68542fca71d4d6a47e18af9fdb217435e31030a130757b.
Keep all108raw queries; use the existing admitted_all mask without modification.
Complete-point indices follow original ascending source IDs; sort them by
SHA256('331/hold/index'), first9held and remaining28sorted train. Save split
and source IDs before any camera scoring. No held-dependent adjustment.

Reuse exact camera_values/cameras/initialize/evaluate/controls function ASTs
from archived0383source, with its offline/private-read guard and shared math.
Do not execute its installer, observation intake, controller or module entry.
Same f1280 seed, E1.5/RNG331, >=90% recoverPose combined support, identity
anchor/unit baseline, f640..5120, TRF100 softL1scale1.5, analytic Jacobian,
1e-8 tolerances; same nonbound/proper/positive and held predictive3px gates.
One bounded worker <=180seconds/2GiB for controls, initialization and evaluation;
no retry after scientific failure. Engine failure is recorded, not hidden.
Save all E/inlier/pose evidence before stops; add descriptive depth/parallax
diagnostics from saved poses even on seed rejection, without alternate solve.
If optimized state exists, record raw Jacobian singular values/rank and training
residuals; no rank-based optimization change. Held score only after initialization
passes. Controls check exact triangulation/OpenCV and wrong camera. At most
PARTIAL_SUCCESS; medical2mm/fullhead/user visual acceptance remain UNVERIFIED.

On failure preserve compact evidence, source and recovery commit, then delete
exclusive runner/loose outputs after archive verification and protected hashes.
Run retained tests; separate cleanup commit. No other route in this budget.

## Actual result: REJECT at held predictive geometry, not count or initialization

Preregistration704d938; frozen runner7341390. Split saved before solve:
held complete indices22,10,25,24,19,14,29,28,17, corresponding original
query IDs61,15,69,68,46,29,79,78,38. Remaining28all used, no pruning.
Observations SHA9784ddc07cbba5b2d96e07959d6d196cc6e782609347878a4a9c04fdc602a57e.

One worker completed1.875s, conservative process-tree peak105402368B.
Both seed pairs had27/28E inliers, all27passed recoverPose support;
all28train points triangulated in front of both seed cameras. Seed median
parallax52.369/14.035degrees is descriptive under assumedf1280, not measured
true motion. Optimization converged byftol after60evaluations, f1199.776568px
inside unchanged bounds. Trainingp95=.786677px. Raw unweighted Jacobian
rank96/96 (168rows), singular min/max4.540596/7612.926157; rank is local
numerical evidence, not proof of global identifiability or true focal accuracy.

All9held points were evaluated without filtering. Predictivep95 by view:
0=.325038px,1=3.798079px,2=2.424998px. View1fails unchanged3px.
Largest view1error4.821992px is originalquery38 (source448,608); its view2
error2.910837px. The other8view1errors are<=2.262209px. This concentration
does NOT authorize dropping that point or using8held instead of9; it also
does not establish thatquery38alone is a false match rather than camera,
triangulation or expression/model error. Small9-point p95 is interpolated.
Allheld depths positive, matrices proper, wrong-camera controls94.888/102.330px.
Exact synthetic triangulation/OpenCV controlmax2.274e-13px, wrongcamera132.927px.

New evidence: these observations support the existing initializer and a converged
camera solution, unlike previous seed/count-only stops. However the frozen
rigid/shared-focal model plus observations does not predict every held view
within tolerance. This rules out count and initialization as THIS run's failing
stage; it does not isolate correspondence error vs nonrigidity vs camera-model
bias. No claim of root-cause certainty, medical improvement, accepted camera,
head mesh or likeness. The2mm medical/fullhead/visual gates remainUNVERIFIED.
Potential reusable part: hashed archived observations and successful backend
execution as a diagnosis fixture, not a production camera or promoted matcher.
No new neural forward, scan/case002 read, image extraction or second solve.

Archive: assets/private/closed-experiments/0385-archive-geometry/evidence.zip,
22546bytes,21members, SHA7e5bc84d7e3cff0c5fab9078e8c61e6632b923bdc0d46d30c6a3b0f1822af1ec.
Contains split, seed/depth/rank/control/held evidence, execution receipt/log and
runner;0383original archive remains intact. CRC/allmember SHA and all9protected
file hashes verified. No new weights/environment were installed. Beforecleanup
167shared tests passed9.018s. No rerun or threshold adjustment permitted here.

Next useful discriminator is independent image-local evidence for the fixed
held residual, not more BA iterations or hiding the worst point. Such diagnosis
must keep the original held score frozen and cannot use scan geometry to repair
the result. No further experiment is executed under this once-only allowance.

## Verified cleanup

Source/result recoveryd440afa. After terminal worker receipt and live process
check, removed exact resolved0385loose directory (20files,24207logical bytes)
and its one exclusive tracked runner. No weights or environment to remove.
All21archive members/CRC/SHA and9protected hashes verified again after deletion;
0383archive unchanged. No tracked live caller remains. Postcleanup167shared
tests passed8.656s. Original0207untracked change untouched. Closed14:15UTC,
within14:28:35deadline. Full task remains unfinished; no accepted head.
