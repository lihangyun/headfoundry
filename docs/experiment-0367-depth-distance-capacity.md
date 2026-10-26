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
