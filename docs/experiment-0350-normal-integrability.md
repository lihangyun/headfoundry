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
