# 0368 physical four-parameter distance fit

Preregistered 2026-10-26, following completed0367cleanup1b0ef9a.
Single change: optimize log(f),log(s),b1,b2 directly instead of seven
independent lifted terms. Same frozen0367inputs and deterministic stress;
all780pairs, no pruning, multistart or noise/threshold sweep. No models,
patient inputs, training or scan access. This tests constraint enforcement,
not actual head quality or a depth network.

Residual: squared pairwise distances of corrected clouds X and Y, divided
by fixed median squared raw-depth difference (floor1e-6). TRF linear loss,
initial f1000,s1,b1=b2=0; bounds f[200,5000],s[.1,10],
b1[-min(d)+.01,10],b2[-min(e)+.01,10]. max_nfev200,
ftol=xtol=gtol1e-12, x_scale='jac'. One start per exact/stress control.
Reject depth-constant input (range<=1e-12), optimizer nonconvergence,
bound contact within1e-6 or nonpositive depths. Physical square/product
relations hold by construction; this is not independent validation.

Exact gate: relative focal<=1e-6, rotation<=1e-6rad, true point alignment
p95<=1e-6sceneunits. Fixed stress gate: relative focal<=.02 and true-point
projection p95<=3px in both views. Proper SVD alignment, same truth-only
evaluation as0367. Plane negative must reject. One60s/1GiB worker. If any
gate fails, stop and close out exclusive runner; retain compact evidence.
Even success only admits this synthetic mechanism for further validation.

## Result: TECHNICAL_CHECK_PASSED, synthetic capacity only

One worker1.390s, conservative tree peak97730560B, exit0. Exact case9
evaluations: f1199.999999999999, alignment p95 1.04e-15sceneunits.
Fixed stress10evaluations: f1196.884869 (relative error0.259594%),
scale1.19913864, shifts.31874677/-.18051464, projection p95
.79390617/1.15357515px, alignment p95 .00651069sceneunits.
Both solves converge without bound contact. Constant-depth negative refused.
All167shared tests pass in8.280s. No patient geometry or medical accuracy result.

Compared with0367's identical stress, enforcing square/product coupling plus
nonlinear physical-distance fitting removes the gross failure in this fixture.
This is a mechanism-level comparison, not an isolation of constraint effects
from changed objective scaling/optimizer. One fixed fixture does not establish
general robustness, nonplanar identifiability or statistical performance. The
negative tests constant-depth rejection only, not all planar degeneracies.
All points participate in fitting; this is not held-out generalization.
Small distances/collapsed configurations and real spatially varying depth bias
remain risks. Do not promote this directly to a production camera initializer.

Protocol deviation: source/document were saved and staged before execution,
but the attempted pre-run Git commit failed from shell argument quoting.
The unchanged source was committed afterward as2097d18. No rerun or parameter
change was made to compensate; do not represent2097d18 as a pre-run commit.
Private result SHA256d7039ec154aac382692b9d080244dc24d1c120a45a0ad0c0d8d80e8bab6caa13;
worker receipts and result remain in assets/private/constrained-distance-0368.
Frozen inputs stay in0367 at its documented hash. Retain this successful
conditional checker; it is not a failed model integration to delete.

Next gate: preregister independent geometry/held-out projection and degeneracy
controls before model installation, then assess actual axial-depth and material
correspondence errors independently. Keep0332's demonstrated photometric
refinement as a conditional backend, not a remedy for wrong correspondences.
No full head fitting until camera/correspondence admission. Medical2mm and
human visual acceptance remain UNVERIFIED; overall goal remains unfinished.
