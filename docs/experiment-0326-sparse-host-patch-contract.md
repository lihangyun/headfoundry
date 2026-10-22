# Experiment0326:sparse host/target direct-patch graph contract

Registered 2026-10-22T19:14:20Z;whole900s,deadline 2026-10-22T19:29:20.000Z. Previous
0325fixed known-camera recipe is REJECT and completely retired at4d95bec.
This implementation step is not a new calibration model or a head fit.

Evidence/hypothesis:0321stopped at a requirement for48complete six-view
tracks,before its geometric/direct solver ran. Real visibility need not make
every point visible in every view. DSO's published residual instead attaches
each point to a host and a set of visible target frames(Eq4-8,Sec2.2,
https://arxiv.org/html/1607.02565v2). This motivates a sparse observation graph,
NOT a claim that stock DSO bootstraps unknown intrinsics. No old0321matches,
solver,fixture,threshold reduction,checkpoint or failed integration is restored.

Single variable:replace0320's complete host0-to-all-target Cartesian residual
with explicit immutable(point,target)observations and arbitrary host IDs.
Reuse unchanged0320projection/interpolation/exposure math for grouped pairs.
For world-to-camera poses E_h,E_t,use E_t@inverse(E_h). Relative log gain
is a_t-a_h;relative bias is b_t-exp(a_t-a_h)*b_h. One positive inverse depth
per host patch remains a local frontoparallel approximation. Native720x1280,
integer centers359.5/639.5,xright/ydown/zforward,shared unknown square focal.
Return values in the exact supplied edge order,not sorted camera order.

Graph IDs must be integer,in range,nonempty,unique,no self edge,no orphan
point. All supplied poses/images/depths/exposures must be finite and valid,
even if a camera has no edge. Included invalid support/depth/exposure fails
closed;missing graph edges are not dynamically pruned residuals. Connectivity,
rank,initialization,visibility correctness,rolling shutter and true unknown
camera recovery remain independent caller admission requirements. No solver
or input-derived graph is implemented or admitted by this contract alone.

Controls:complete-graph equivalence to0320;analytic affine-intensity translated
plane with nonzero host exposures and sparse multi-host visibility;independent
OpenCV projections under noncommuting host/target rotations;globalSE3and
affine photometric gauge invariance;negative graph/domain/nonfinite tests.
Float64algebra tolerances do not relax actual3pxor2mmgates. Run full retained
suite under120s. Stop on failed control/resource/deadline;no seed,threshold,
scene or precision sweep. If pass,retain minimum opt-in arithmetic/regression
only. If fail,record evidence/Git recovery and retire exclusive failed files
before any different route. No package/model/private media/scan/case002read,
training/upload/default/source-asset change. Protected files remain unchanged.
All actual-camera/head/medical precision/likeness acceptance stays UNVERIFIED.
