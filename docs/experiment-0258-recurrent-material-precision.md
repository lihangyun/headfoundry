# Experiment0258: recurrent material-tracker precision prerequisite

Date:2026-10-20. Pre-registered before download/install/inference. UNVERIFIED.
0257 closed at3aba4fa with insufficient certified distributed material points;
0256's silhouette family and earlier local LK/patch/descriptor variants stay
closed. No head/camera gate is waived by adopting a different observation model.

## Different mechanism and licensing

Test frozen **TAPNext++256** recurrent transformer inference,not another local
patch window,pyramid,flow threshold or silhouette solver. Temporal learned
state and global image tokens are different information processing from the
retired local trackers. The hypothesis is only that this model can preserve
native source-pixel material locations accurately enough to merit a later
physical-video correspondence screen. Benchmark AJ/survival is not evidence
for our1px localization or3px physical-camera requirements.

[Official source](https://github.com/google-deepmind/tapnet/tree/730cda1c730877cfedbe01bf87fb1cadb78a565d)
and [explicit checkpoint license](https://github.com/google-deepmind/tapnet/blob/730cda1c730877cfedbe01bf87fb1cadb78a565d/tapnet/tapnextpp/README.md#license)
declare Apache-2.0. Source/weight hashes and provenance are locked in
`examples/tapnextpp-0258.asset-lock.json`. CoTracker's predominantly NC code is
excluded,as are unreviewed alternative checkpoints/datasets and cloud demos.
Download only the reviewed3 inference modules plus license/readmes;do not run
the package installer that pulls JAX/training/data integrations. Use a dedicated
CPU environment with pinned permissive Torch/TorchVision/einops dependencies;
leave the shared environment/defaults unchanged. No training or upload.

## One main variable and source-only fixture

The candidate correspondence extractor is the sole main experimental variable.
Do not tune resolution,checkpoint,precision,query density,frame sequence or
visibility thresholds in response to errors. This is a necessary image-space
precision screen,not real3D motion,a complete-video track,camera or head result.

Read only exact sequentialcase001 source ordinal0,verify full RGB digest against
0252 and use the unchanged0257 native crop[160,400,600,900] (440x500). No skin,
bone,case002,manual candidate IDs or known3D conditioning. Generate9 fixed
analytic planar image warps from that crop with OpenCV linear sampling and
reflect101 borders. Warps are validation inputs,not synthetic training data.
For each row below,H=T(tx,ty) C P R(angle,scale) inv(C),where C translates to
native pixel-center(219.5,249.5),P has bottom row[p,q,1],and R is the ordinary
2D counterclockwise rotation/scale matrix. All values are fixed before inference.

| Frame | Angle degrees | Scale | tx | ty | p | q |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| 1 | 0 | 1 | 4 | -3 | 0 | 0 |
| 2 | 3 | 1.01 | 8 | -6 | 0 | 0 |
| 3 | 6 | 1.02 | 12 | -9 | .00005 | -.00003 |
| 4 | 3 | 1.01 | 8 | -6 | 0 | 0 |
| 5 | 0 | 1 | 0 | 0 | 0 | 0 |
| 6 | -3 | .99 | -8 | 6 | 0 | 0 |
| 7 | -6 | .98 | -12 | 9 | -.00005 | .00003 |
| 8 | 0 | 1 | 0 | 0 | 0 | 0 |

Query all64 native grid points(x,y)=(80+40*i,120+40*j),i,j=0..7 in crop space.
No detector/texture/confidence/error filtering. Retain all512 non-query
point-frame evaluations;report the64 frame0 self-query errors separately.
Analytic transformed coordinates stay evaluator-only. The model receives9 RGB
frames and64 frame0 queries,not H,target tracks or candidate marks.

The TAP convention is(t,y,x) and returned(y,x),raster-corner units. Convert our
integer-center xy by(+.5)*256/[440,500],then swap;invert with swap,*[440,500]/256
and-.5. Check asymmetric xy/half-pixel/warp inverse controls before the run.
Resize to256x256 with linear sampling,normalize RGB to[-1,1],CPU float32,
8 threads,eval/inference mode,online one frame at a time,strict state loading,
weights_only=True,no compilation,AMP,query reset or downstream patch refinement.
Read the checkpoint with memory mapping to avoid an unnecessary full-file memory
copy;this changes neither weights nor numerical precision.

## Gate,budget and stop

All non-query frames must have finite64-point results,p95 native error<=1px,
maximum<=3px and predicted-visible fraction>=.95 using the frozen official
logit>0 rule. Identity returns5/8 must meet the same gate. Report all original
points even if visibility predicts otherwise. No fitting a post-hoc homography,
offset,axis choice or point subset to improve the score. Image interpolation is
part of this exact configuration,not a license to retune after failure.

Setup/download has15minutes wall time measured from first installation/download;
checkpoint is2532282370bytes (2.53decimalGB),one exact hash,download capped10min.
One9-frame inference process including load is capped300s. Engineering fixes
only for demonstrated implementation/convention errors before a valid run;
no checkpoint/resolution/precision/seed rescue. Record actual elapsed wall time
and hard-stop on unsupported license/hash/load,resource budget or failed gate.

Failure closes this exact recurrent configuration before real-video cameras or
head fitting. Keep a compact report,source/weight hashes,recovery commit and
at most two diagnostic panels;remove its exclusive runner/tests/weights/source/
environment and raw warps/predictions after verification. Success is only
TECHNICAL_CHECK_PASSED planar precision,and still requires independent3D
visibility/rigidity,real-video applicability,distributed held correspondences
and original camera/head/scan/visual gates before any accepted head claim.

## Actual result: conditional precision pass,not3D recovery

Preregistratione163886;runner recovery4210722 plus subsequent evaluator-only
hash/analytic-truth guards. One inference,not a checkpoint/resolution sweep.
Setup was independently verified complete within472.197s wall time (an upper
bound including implementation/inspection),below900s. The complete downloaded
2532282370byte file matches the locked SHA256;the download code enforces600s.
Its captured asynchronous stdout was unavailable,so no exact download duration
is invented. Installed runtime imports and `pip check` pass. Fifteen installed
package versions/license notices are recorded locally;Jinja2's license metadata
field is empty,but its actual bundled LICENSE.txt is BSD-3-Clause. No JAX,
training/data pipeline or recurrentgemma installation is needed by reviewed
inference imports. Main environment remains unchanged.

Strict load has zero missing/unexpected keys,194202881 parameters. CPU float32
inference takes27.855s including verification/load;the hard-timeout parent
finishes normally in28.954s,not300s. Per-frame inference is1.89-2.12s. No AMP,
compile,source substitution,query reset,post-hoc bias/axis fit or pruning occurs.
All target/visibility populations and input/output/source hashes are retained.

| Frame | p95 native px | Max native px | Predicted-visible fraction |
| --- | ---: | ---: | ---: |
| 0,self-query only | .743898 | .774941 | 1.0 |
| 1 | .470346 | .559534 | 1.0 |
| 2 | .596857 | .686298 | 1.0 |
| 3 | .699244 | .884103 | 1.0 |
| 4 | .640644 | .749221 | 1.0 |
| 5,identity return | .513086 | .575985 | 1.0 |
| 6 | .519089 | .857288 | 1.0 |
| 7 | .562434 | .701261 | 1.0 |
| 8,identity return | .723442 | .985245 | 1.0 |

All8 non-query frames pass the predeclared1px p95/3px maximum/.95 visibility
gate,with all512 observations counted. Independent evaluator recomputes all
analytic homographies/targets and verifies hashes against pre-inference input
and post-inference output records. Asymmetric axes,half-pixel conversions and
warp inverses pass;132 current tests pass in5.050s before evaluator hardening.

Actual source-only panels for predeclared maximum-rotation frame3 and final
identity return8 were inspected. Points stay on the displayed source appearance;
right-hand arrows are explicitly magnified20x for diagnostics. These pictures
are synthetic **2D warps of the real video**,not generated3D heads,3D rotation,
new anatomy,scan overlays or independent clinical evidence. No likeness claim.

Status:TECHNICAL_CHECK_PASSED **planar precision only**. Camera/physical material
rigidity/3D/head/visual acceptance remainUNVERIFIED,not PARTIAL_SUCCESS or ACCEPT.
Next independently test actual known3D rotation/visibility before transferring
this model to real-video camera fitting. Keep this small positive fixture and
locked local candidate/runtime for that gate;do not restore any rejected model.
No failed-route cleanup is triggered by this positive prerequisite,which does
not imply the overall tracker/camera route has passed. Private evidence remains
at `assets/private/recurrent-material-0258`;no human material is uploaded/trained.

Post-inference evaluator hardening does not rerun or alter predictions:it rejects
changed input/output/analytic-truth identities. The assertion-based experimental
diagnostic also refuses Python-O entirely,so optimized execution cannot bypass
rights/hash guards. This is regression-tested without human data or a model.
The dedicated environment is explicitly Git-ignored;private fixtures/weights
remain ignored under the existing rule. Final protected10 source/consent files,
original video and0230 known-motion fixture hashes are unchanged. No production
code/default or case002 source changes occur. Final tests and evidence inventory
are recorded privately in `tests-final.json` and `verification.json`.

Final132 tests pass in6.885s,including the optimized-mode rejection. With the
already installed,hash-locked local assets,the exact three-stage replay is:

```powershell
.venv\Scripts\python.exe tools\check_recurrent_material_0258.py prepare
.venv-tap0258\Scripts\python.exe tools\check_recurrent_material_0258.py infer
.venv\Scripts\python.exe tools\check_recurrent_material_0258.py evaluate
```

Inference is the middle stage only;its caller must enforce the registered300s
process timeout,as recorded in private `inference-invocation.json`. Do not run a
second model trial merely to recreate the report. Source/license/checkpoint
identities and exact runtime versions are in the public asset lock;required
local permissions and fixtures are not distributed with the repository.
