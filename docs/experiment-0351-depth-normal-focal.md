# 0351: independent inverse-depth cue plus normals

Registered2026-10-24 after0350cleanup6211aff,before execution.
One new information source:affine inverse depth p,with1/z=s*(p+k),unknown s,k.
Unlike0350,this constrains the depth graph independently of the normal field.
No restored normal-only runner,no pretrained model,patient or scan input.
Use the same two explicitly defined original analytic graphs/grid from0350;
implement anew the different two-unknown equations,not parameter sweeps.

Let D=a*x+b*y+c*f. Orthogonality implies p_x*D=a*(p+k),
p_y*D=b*(p+k),hence stack linear equations in[f,k]:

    [c*p_x,-a] [f,k]^T = a*p-p_x*(a*x+b*y)
    [c*p_y,-b] [f,k]^T = b*p-p_y*(a*x+b*y)

Synthetic input p=1000/z-.7,analytic normals,truef1200. Estimator receives
only x,y,p,n;finite differences of p at step2,drop fixed2gridcell border.
Column-normalized SVD/lstsq,rank2required with singular ratio>1e-8;
finite positivef and p+kpositive. No focal/shift priors or truth to estimator.
Exact controls:both curves recoverf within2%,k within.02;plane rejected;
normal/tangent dot products<1e-12. Fail any control:stop and clean this recipe.
One fixed1degreeXnormal bias as0350:report errors and positive-depth status,
but do NOTinterpret it as the actual pretrained error distribution. Its result
cannot relax eventual3px/2mmgates. It is diagnostic,not a model-validation pass.

Whole10minutes,one60s/1GiB monitored worker. No optional smoothing,weights,
pruning,seeds,crop changes or multiple configurations. Save full scalar results
and SVD/rank evidence. TECHNICAL_CHECK_PASSED means only algebraic capability;
model coordinates,depth affine convention,principal point/distortion and actual
prediction error remain UNVERIFIED. No camera/head promotion or model download
from this alone;next would require pinned source/convention and in-domain tests.

## Actual evidence and decision

One bounded worker0.547s,69,398,528B conservative tree peak,exit0.
Exact-input algebra controls TECHNICAL_CHECK_PASSED:quadraticf1199.984846,
k.699980006;sinusoidf1200.055559,k.700027958;plane unidentifiable as expected.
Column-normalized smallest singular values .0096153/.0220352 establish rank2
for these particular noiseless inputs,not noise robustness. Tangent controls
are below1.12e-16. This demonstrates the added cue changes identifiability;
it is not another run of the rejected normal-only estimator.

The diagnostic1degree coherent normal bias produces focal58.986172/146.182525
(95.0845%/87.8181%errors). Quadratic recovered inverse depth becomes nonpositive;
the sinusoidal case retains positive depth despite its very wrong focal.
Consequently positivity and algebraic rank cannot certify physical accuracy.
The bias examples were diagnostic,not a preregistered pass/fail criterion;
do not relabel the successful algebra control as failed. However these measured
sensitivities provide no basis to spend on a pretrained-model camera trial.
Engineering decision:REJECT direct two-cue calibration as a ready initializer;
DAViD itself remains NOT_RUN/UNVERIFIED,not rejected on unmeasured model accuracy.
No model weights downloaded and no threshold/precision/conditioning sweep.

Full compact result and resource receipts remain in
assets/private/depth-normal-0351/{result.json,worker.json,worker.log}.
Result SHA256 to be recorded with closeout. Source recoverya8f5ff1.
Real video camera,metric scale,medical2mm and complete head remain UNVERIFIED.
Before any different route,retire this exclusive experiment runner;preserve
the small complete report as evidence. No data/model/runtime cleanup required.
