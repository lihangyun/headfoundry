# 0350: independent normal-integrability focal check

Registered2026-10-24 before numerical execution. One analytic experiment,
10minute whole budget,worker60s/1GiB;NumPy only,no models,patient data or scans.
Single new information source:known camera-space normal field,not shading,
material tracks or pretrained camera prediction. Formula is in audit0349.

Fixed grid x=-240..240,y=-320..320,step2pixels;truef=1200.
Two original smooth depth graphs in arbitrary consistent length units:
z1=800+.0004x^2+.0002y^2+.0003xy;
z2=800+30sin(x/140)cos(y/190)+.0002x^2.
Construct normals from analytic depth partials using
n=(-f*z_x,-f*z_y,z+x*z_x+y*z_y),then unit normalize.
Estimate normal partials by centered finite differences,exclude only the
fixed two-pixel-grid boundary. Solve scalar least squares f=-dot(A,B)/dot(A,A).
No optimizer,priors,bounds,scan scale or truth supplied to estimator.

Controls:constant normal must be flagged degenerate;exact integrability must
recover both focal values within2%. Independently check normals orthogonal to
analytic surface tangents. Report equation RMS,all focal values and errors.
One fixed stress condition:rotate all normals by+1degree around cameraX,
holding image coordinates fixed. This is NOT a physical camera rotation;
it is a coherent normal-prediction coordinate bias. No random seed/sweep.
If either stressed focal error exceeds2%,do not download DAViD on the premise
that this direct formula gives reliable camera calibration. Record sensitivity
and stop this recipe. This engineering screen is not a statistical estimate
of DAViD bias or proof that every regularized normal method fails.
Even success is only TECHNICAL_CHECK_PASSED,never head/medical acceptance.

## Actual result and degeneracy audit

One execution0.330s,exit0. Result REJECT for this direct calibration recipe.
No model downloaded or run. Exact normal/tangent orthogonality<1.12e-16.
Constant-plane control correctly degenerate. Sinusoidal graph gives1200.0773px
(0.00644%error);with fixed1degree bias1195.1340px(0.4055%error).
Quadratic graph gives13.3881px and1977.8311px under bias;neither is trustworthy.
Its nominal A-energy1.788e-13 is numerical differencing residue,not true signal.

Important correction to the proposed test interpretation:curvature does NOT
imply focal identifiability. For any homogeneous quadratic Q,z=C+Q,unnormalized
normal=(-f Q_x,-f Q_y,C+3Q). Mixed-partial symmetry gives b_x-a_y=0,and
a*c_y-b*c_x=0,so A=0 exactly. Euler's identity H(Q)[x,y]^T=grad(Q) gives B=0
exactly too. Unit normalization multiplies A/B by the same scalar squared;
it cannot restore rank. Every focal value satisfies the local integrability
equation for this family. The fixed1e-24energy check missed that finite-
difference degeneracy;do not fix it by a threshold sweep or claim13px is an
identified physical answer. The second surface demonstrates a nondegenerate
conditional case,not generally reliable video calibration.

This evidence closes the unqualified direct normal-to-focal initializer.
It does not reject the DAViD model nor prove all normal-assisted methods fail.
A future materially different method would need independent metric/projective
information or a validated uncertainty/rank treatment,not merely more precision.
No permission to proceed to head fitting follows.3px/2mmgates unchanged.

The whole run was small;the planned60s/1GiB hard worker monitor was inadvertently
not used. Only elapsed time is recorded by the terminal;peak RAM is unverified.
Do not call this a resource-budget verification pass or rerun to rewrite history.

Compact complete evidence is the small local JSON at
assets/private/normal-integrability-0350/result.json. No dense output was made.
Source recoverybe5fe99. Retire the exclusive checker after recording this result;
retain the report as necessary evidence,not an active failed runtime. No original
or successful fixture was modified. No new head or medical precision result.
