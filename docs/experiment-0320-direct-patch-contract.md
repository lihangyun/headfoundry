# Experiment0320:independent direct-patch camera residual contract

Registered2026-10-22T16:22UTC after screen c8f8f17,before new code/tests.
Whole900s to16:37UTC. Previous source screen is progress:excluded unlicensed/
circular-prerequisite stacks and identified the direct-patch hypothesis without
installing them. This step implements the coupled residual needed to test that
hypothesis;it does NOT fit/admit a camera,head or physical2mmresult.

Single implementation variable:photometric patch observations coupled by shared
unknown focal,free targetSE3and per-point inverse depths,with per-image positive
gain/offset. Anchor pose/exposure fixes gauges only. One depth per anchor patch
is a local frontoparallel approximation,NOT known head geometry. No fixed pivot,
medical mesh,SHlighting or independent per-point2Dendpoint optimizer. This is
independently written arithmetic,not copying DSOor0251code or restoring a stack.
Reuse retained native bilinear-grid and shared camera projection math;no new
package/model/weight/training/upload/patient/scan/case002content/default change.

At every target pixel,r=I_target(project(K,T,X))-b_target-
exp(a_target-a_anchor)*(I_anchor(pixel)-b_anchor),with X=K^-1pixel/rho.
Native integer centers/720x1280,xright/ydown/zforward;center359.5,639.5.
Finite proper matrices,positive depth/gain and full bilinear support required.
No out-of-frame/depth clamping,visibility pruning,missing patch deletion or
silent exposure overflow. This valid-domain primitive is not yet a complete
optimizer;future solver bounds/barriers/occlusions require separate registration.

Independent analytic controls:translation of a known frontoparallel plane with
an affine intensity ramp plus positive gain/bias must give zero residual;
nonzero rotation/translation projection must replay OpenCVprojectPoints;gain/
bias derivatives and independently varied focal/depth/state sensitivity checked.
Reject invalid/NaN/empty/nonpositive/reflected/off-image inputs. Unit tolerances
cover float64algebra only,not arbitrary neural or physical accuracy thresholds.
Run retained suite under120s;no parameter/seed/precision sweep. A pass retains
only minimum pure math and its regression,clearly marks physical camera/head
UNVERIFIED,and permits design of a separate full unknown-camera capacity test.
Failure stops,with compact evidence/source recovery and exclusive cleanup.
