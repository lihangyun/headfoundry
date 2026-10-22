# Experiment0328:direct shared-focal relative-pose solver admission

Registered 2026-10-22T19:28:24Z;whole1200s,deadline 2026-10-22T19:48:24.000Z.
Previous0327REJECThas finished independent cleanup9ea7138. No prior failed
implementation/weights/runtime or hidden scan/patient seed is restored.

Source inspection of unchanged short_track_camera has not proven a sign or
coordinate implementation bug. Its method first fits unrestrictedF,then
enforces essential singular values to inferf. Hypothesis:direct six-point
shared-focal pose hypotheses with joint robust refinement can avoid that
sequential nuisance estimate. This is an algorithm change,not another bound,
precision,threshold,count or seed sweep of the failed initializer. Source
evidence:PoseLibv2.0.5robust.h shared-focal estimator;official README recommends
this over focal decomposition for same-camera pairs. Whether it helps this
video remains unverified. Existing docs/code have no prior PoseLibintegration.

Pin one official PyPIWindowsCPython3.12wheel:poselib2.0.5,
poselib-2.0.5-cp312-cp312-win_amd64.whl,
SHA256e2db979ac77db14c89e3f07f4bd6fb5ac61dbacfc3634a8ae462964a4ac7f1f7.
BSD3source/binary grant at official v2.0.5LICENSE;retain attribution/no-endorsement
and disclaimers. Resolve tag and archive source identity/grants;wheel provenance
is publisher SHA,not a reproducible-build or patent/FTO claim. Inspect exact
embedded grant,metadata,allRECORDhashes,safeZIPpaths and Python entry before
import. Extract in one private overlay only;no main-package install or fallback.
Existing NumPy/OpenCV/SciPy only,no NNmodel/checkpoint/account/training/upload.

First software/conditional precision test is NOT image-to-head success. Owned
seed328fixture:120XYZuniform[-.45,-.8,2.5]..[.45,.8,3.5],native720x1280,
truef1200,integercenter359.5/639.5. AnchorI;targetR=Ry18deg@Rx15deg,
t=(0,0,3)-R@(0,0,3). Estimator receives only96pairedXYand principalpoint,
not K/XYZ/R/t/truth or held24points. Common square focal/center are assumptions,
not verified phone intrinsics. One exact case then one fixed case with .5px
Gaussian coordinate noise in both training views and last20target rows cyclically
permuted among themselves. No scene/seed/noise/outlier/model/options sweep.

Use estimate_shared_focal_relative_pose once/case,seed328,max10000RANSACiters,
max_epipolar_error1.5px,success probability.999;other options record defaults.
No initial pair/pose/focal prior or manual result selection. Keep raw cameras,
R/t,inlier masks/stats,all input hashes and output before truth evaluation.
Validate proper finite SE3,positive finite sharedf,unittranslation;normalize
translation only for evaluation scale gauge using known baseline length.
Require exactfrel<=1e-5/heldknown3Dprojectionp95<=1e-3px,noisyfrel<=2%and
ALL24heldknown3Dprojectionp95<=3px in EACH view;no held-point pruning. All
held positive depths,OpenCVprojection replay<=1e-9px,and wrong+.1rad-camera
negative control must fail3px. Exact failure stops noisy case. Noiseless pass
is software evidence only;noise pass is ONE conditional precision result.

Acquisition<=120s/256MiB,worker<=120s/2GiB,full retained suite<=120s;whole1200s
includes source review/implementation/cleanup. Four math threads,existing full
descendant-tree budget,no duplicates. Inference read audit denies truth/STL/
unrelated private files/network/subprocess(cooperative,not hostile sandbox).
Failure:report/source/hash/compact raw evidence,retire exclusive runner,
binary overlay/wheel/cache and tests before a different method,independent
cleanup commit. Pass:retain only opt-in verified asset lock/entry and a minimal
replay;unknown global multiview consistency/real-video/medical/head/likeness
remain UNVERIFIED. No production defaults,shared sources,0207or case002change.

Primary sources:https://github.com/PoseLib/PoseLib/tree/v2.0.5,
https://raw.githubusercontent.com/PoseLib/PoseLib/v2.0.5/LICENSE,
https://pypi.org/project/poselib/2.0.5/.

## Pre-import grant-text format correction

First acquisition c0dddc0downloads the exact wheel and five tagged source files,
validates wheelCRC/RECORDbut stops6.172s/117637120bytes before extracting/importing:
wheel grant containsCRCRLFwhile source hasLF. Raw wheel/source hashes differ
as expected;manual text inspection identifies no word/content difference.
Retain original bytes/hashes and the failed worker/log. Canonicalize ONLY
CRCRLF/CRLF/CRtoLFfor full-text equality,not copyright/terms/whitespace words.
Finalize the already hash-verified local bytes without redownload/solver call.
This is pre-execution packaging repair,not a physical threshold/precision change.
Record the effective wrapper bundle loss_scale.75(.5*1.5)rather than misleading
unmodified class default1.0;no solver has run and registered behavior is unchanged.
