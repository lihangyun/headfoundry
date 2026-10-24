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
