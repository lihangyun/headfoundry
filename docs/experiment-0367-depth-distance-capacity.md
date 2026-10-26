# 0367 independent lifted distance solver capacity

2026-10-26 preregistration. One NumPy/OpenCV check before any model download.
Original0366seven lifted variables, column-normalized linear least squares
rcond1e-12; no nonlinear refinement, robust pruning or initial camera guess.
Single hypothesis: two affine axial-depth observations plus corresponding
pixels identify shared focal using rigid pairwise distances without pose seeds.

Fixed original fixture: RNG367,40points x/y uniform[-.6,.6],z[2.5,3.5],
rotation Rodrigues(.12,.22,-.04),translation(.18,-.08,.12),f1200,centered pixels.
Depth inputs d1=z1-.3 and d2=z2/1.2+.2. Estimator receives only pixels/depths.
All780point pairs enter. Column-normalized rank7required (1e-12cutoff).
Require positive f²/s² and corrected depths, nonlinear lifted consistency
relative error<=1e-6, exact focal relative error<=1e-6, reconstructed relative
rotation error<=1e-6rad and translated points p95<=1e-6sceneunit. Original
independent Rodrigues transform supplies evaluation only. No medicalmm claim.

Rigid pose uses proper SVD alignment of the corrected clouds. Negative control:
same x/ybut constant first-viewz3 must fail rank7,not yield an accepted camera.
One fixed stress: add0.5px*sin(arange) to each pixel component and0.005*sin(arange)
to each depth array (different offsets per view); this is a deterministic probe,
not a realistic model-error distribution. Report rank,positivity,consistency,
focal and alignment error even if failed. Stress admission needs original2%focal
and3px true-point projection at both cameras; no relaxing lifted consistency.
Failure of either exact or stress admission stops this specific linear recipe;
it does not reject all depth-assisted methods or untested pretrained models.

One bounded60s/1GiB worker; no human/scan/old predictions, weights or packages.
Source recovery commit before execution. Save full scalar result and original
small numeric inputs. No seeds/noise/threshold/precision sweep. On failure keep
compact evidence and remove exclusive checker before any different route.

## Result: REJECT the unconstrained lifted linear recipe

Source8d3fda6. One worker0.547s/58245120B conservative process-tree peak,exit0.
Exact input: rank7, focal1200.0000000000011, scale1.2000000000000042,
shifts0.30000000000000976/-0.20000000000001056. Nonlinear consistency3.39e-14,
alignment p95 1.32e-14scene units; projection p95 2.84e-13/1.57e-12px.
Plane control refuses its zero column. These establish conditional algebraic
capacity only,not noisy-data utility or a pretrained depth-model performance.

Fixed stress: rank7 and positive corrected depths, but focal501.767474px,
58.186%relative error; projection p95 177.94794/202.90859px. Lifted consistency
2.251814 fails1e-6 by a large margin. Example:b1=-2.12355 while independently
estimated b1²=5.56216,not the square of that b1. Multiplicative constraints are
similarly violated. Unconstrained lifting relaxes physical algebraic relations;
inexact data need not retain them. This observed mechanism invalidates reading
the linear solution directly as a physical camera. It is not proof that all
noise error is due to this relaxation or that a constrained solver will pass.

Stop without changing cutoff,noise,seed,precision or adding post-result fitting.
No deep model,patient input or reconstructed head was produced. Result JSON,
40point original input NPZ and worker receipts stay as compact evidence in
assets/private/depth-distance-0367. They include the successful exact control;
they are not failed mesh/weight bulk. Full source recoverable at8d3fda6.

Reusable lesson: distance constraints can identify this noiseless configuration;
the seven lifted terms are not seven physically independent parameters. A
future mechanism must enforce their coupled relations during estimation and
verify sensitivity separately. That would need new preregistration,not a claim
that this failed initializer merely needs a different threshold. This finding
does not validate any actual monocular depth source or independent visibility.
