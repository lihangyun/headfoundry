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
