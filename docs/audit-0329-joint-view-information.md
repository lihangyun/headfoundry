# Audit0329:does common-three-view structure break the two-view ambiguity?

Registered 2026-10-22T19:43:57Z;whole900s,deadline 2026-10-22T19:58:57.000Z.
Prior0328closeoutdb91d50is complete. No failed solver/model/runtime restored.
This is a read-only information audit,not another camera fit or easier head goal.

0328proved a continuous two-view focal family.0318already measured improved
but insufficient noisy information on a DIFFERENTfive-view fixture;do not tune
its angles/counts to cross.02or reuse that result as this context's truth.
New question:does a shared3Dpoint across three cameras supply a focal constraint
that independent pairwise essential constraints lack? Single structural contrast:
original0328two-view commonXYZversus those same views/points plus ONE different
axis view,R3=Ry(-18deg)@Rx(15deg),same pivot(0,0,3). No selected angle/seed/count/
noise/focal/geometry/solver sweep. A third copy of view2is a redundancy witness.

Read only0328compact owned-coordinate capsule after SHA/CRCverification:
b36d23d6279c073793e74048fa86caaf3359587ef7f407e50d2e0a648598971a.
Its XYZ/trueK/poses are diagnostic inputs only,never camera initialization or
human inference. Normalize scene and all translations by original baseline
length to preserve the existing unit-baseline parameter gauge. Three contexts
keep original120points and both original poses,all observations included,no
held noise draw/optimization step. No actual video,scan,case002,model,download,
new package,training/upload or default change.

Reuse shared focal_information/linearize;add the minimum analytic native
Jacobian using OpenCVprojectPointsrotation/translation derivatives,closed-form
point and common logf derivatives,and the exact baseline-direction chain rule.
Verify all columns against existing two-step central differences(relative<=1e-7)
and forward replay<=1e-9pxbefore interpreting rank. Proper matrices,finite
inside-native positive-depth support required. Existing rankrcond1e-12unchanged.
Analytic columns prevent finite-difference error from inventing rank in the
proven critical case. Profile logf against ALLfree camera/point nuisances;
anchorSE3and baseline norm fix similarity gauges only,no known pose/point prior.

Required controls:analytic-vs-numerical match,original two-view focal contrast
relative norm<=1e-10and no added focal rank;copied-third-camera same null result;
all original data/gauge preserve exactly in extended contexts. Report actual
third-view rank/profile whether useful or not,no tuning if it remains confounded.
If identifiable,report local sigma(logf)for declared.5pxindependent Gaussian
coordinate noise as a diagnostic only,not achieved accuracy/confidence/global
uniqueness/3pxor2mmacceptance. Copied view's independent-noise precision is not
claimed. Nonzero information does not authorize a patient fit or new stack.

Worker<=120s/1GiB,four math threads,existing descendant-tree monitor;full retained
suite<=120s. Save raw Jacobians/states/ranks/input/source hashes and compact
private archive,no pictures. Retire one-off driver/bulk after read-only audit,
keep only verified generic analytic derivative/regression if correct. Protect
38prior identities and unrelated0207. Stop on domain/control/resource failure,
no tolerance/finite-difference step/angle/point rescue or restored SDK trial.

Derivative API source:https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html
(projectPoints);installed implementation is separately checked numerically.
