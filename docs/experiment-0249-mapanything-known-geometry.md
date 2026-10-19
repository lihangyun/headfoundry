# Experiment0249: one Apache image-only known-geometry screen

Date:2026-10-20. Pre-registered before any image forward.
Execution/replay:TECHNICAL_CHECK_PASSED. Geometry screen:REJECT.
No accepted reconstructed head follows.

Only new variable versus0236 is the reviewed0248 MapAnything-Apache initializer
and its official image preprocessing. Use exactly the six unchanged0230 source
clay images:front,yaw-10,yaw+10,yaw-30,yaw+30,pitch+10. These are **supplied-scan
renders**,not a reconstructed person. case001 only;case002 and bone unused.
No cameras,depth,point correspondences or scans are model inputs. Evaluation
alone reads the frozen known-motion archive. Rights/stage/mm/hash checks precede
execution;no network connections,training or uploads allowed.

PinCPU float32,4threads,seed18;official `load_images` fixed_mapping518,DINOv2
normalization,patch14. `infer`:memory_efficient_inference=True,minibatch_size=1,
use_amp=False,apply_mask=False,mask_edges=False,apply_confidence_mask=False,
use_multiview_confidence=False. No confidence/edge/non-ambiguous row pruning.
One forward only,300s wall-clock budget enforced by parent;save terminal failure
and stop this exact configuration if time/compatibility fails. No precision,
resolution,view/checkpoint sweep or fallback. Asset validation plus model loading
has separate180s budget before the inference timer.

For original720x1280 images derive the exact PIL resize dimensions by upstream
floor(max(target/original)+1e-8),then integer centered crop. Use actual per-axis
resize and pixel-center translation `(scale-1)/2-crop`;check a separately resized
and normalized RGB array equals official input exactly. Never reuse0236's.525.
Intrinsic recovery uses integer pixel centers. Verify C2W convention by actual
camera-point to world-point consistency,proper rotation/positive depth and
recovered pinhole ray reprojection p95<=.5processed px. No guessing inversion.

Reuse frozen0236 camera triangulation/evaluator and support population:front and
yaw-10 triangulate;held+10,-30,+30,pitch+10 each p95<=3original px,all cheirality
and focal400..3000px checks. Also sample **all** front predicted world points at
the fixed original truth pixels and reproject into all five other views with
the same3px gate. No per-view alignment,camera fitting,residual rejection or
scan-to-prediction registration. A global similarity is unnecessary for these
gauge-invariant projection tests. Exact synthetic-camera/point oracles must pass
before learned inference. All failures remain failures,not head ACCEPT.

Only a complete geometry-screen pass permits a separately pre-registered
real-video experiment. Success here would still not establish face accuracy,
complete-head coverage,editable topology or likeness acceptance.

## Actual single-run result and stop

Forward82.631s,total107.258s,exit0,no timeout. All six image tensors reproduce
the official RGB resize/crop/normalization exactly. Output is294x518(WxH)pixels
(actual resize294x522,center crop0,2). All812 checkpoint keys still load strictly.
Exact known-camera/source-point oracles pass before inference. Every requested
joint sample remains:1934,1948,1641,1691,1643;none invalid or removed.

| Held target | Camera-only p95 original px | Front point-map+pose p95 original px |
| --- | ---: | ---: |
| yaw-10 (source pair) | not independent | 25.441 |
| yaw+10 | 10.614 | 18.375 |
| yaw-30 | 20.797 | 57.443 |
| yaw+30 | 36.455 | 42.408 |
| pitch+10 | 13.022 | 15.185 |

Every3px gate fails. Proper rotations,intrinsic format,positive depth and
original focal1618-1639px pass,but cannot override residuals. Actual C2W point
composition agrees to2.04e-7 relative maximum;the matrix direction is not guessed.
Recovered pinhole rays have p95 2.048-2.459processed px,also failing the.5px
internal-consistency gate. Relative rotations deviate.48-6.82degrees.

Compared with0236 camera-only p95(15.50,25.95,93.71,22.29px),all four are lower,
but still fail. Joint point results worsen in4/5 targets,so **no overall accuracy
gain or PARTIAL_SUCCESS claim**. This tests our reviewed MIT-runtime variant on
one supplied-scan clay scene,not all official MapAnything tasks or real photos.
Do not generalize this failure to every model/domain,or transfer it to a real
head simply because some camera numbers improve.

Frozen output evaluator replay returns exact0px difference.207 unit tests and
Git whitespace checks pass. Actual five-row/two-column source-clay projection
sheet was inspected:systematic30deg pose errors and larger boundary/neck point
errors remain. It is visibly labeled supplied-scan diagnostic,not reconstruction.
The sheet displays about100 rows/view for legibility;all populations above,not
the displayed subset,determine metrics. No bad point is pruned from evaluation.

Private artifacts:`assets/private/mapanything-apache-0248/known-geometry-0249/`
contains controls,executed pre-registration,oracle-report,preprocessing,
predictions,all camera/joint residual archives,report,numerical-replay,
known-geometry-review.png,execution capsule and visual review. Weight/source
snapshots and patient-derived images remain outsideGit.

Freeze this exact unconditioned image-only initializer configuration. No real
video fit,new scan-head metric,mesh export,production replacement or case002
use follows. The next gate remains independently reliable camera/material
geometry,not another prior/contour fit or threshold/precision/checkpoint sweep.
