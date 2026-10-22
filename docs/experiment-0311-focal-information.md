# Experiment0311:local focal information before another camera implementation

Registered2026-10-22after verified0310closeout9e579e6,before new computation.
0310demonstrated8.46%focal error/nonconvergence with sigma.5px/axis noise,but
did not distinguish weak measurement information from optimizer failure. Do not
assume a new solver can recover2%focal on an intrinsically weak noisy fixture.

One diagnostic variable:profile Fisher information of log focal after accounting
for all free camera/point nuisance variables,at the exact procedural truth.
Reuse unchanged0310archive SHA02904964cc00551dd15ee1a44cf28e6388508afdb5c89fd08575c1389399352b,
all141tracks/old train fold/true cameras and points. No held row enters information.
Native-center truth K subtracts.5from the fixture's raster-extent principal point.
Transform truth once to the original anchor2/baseline3gauge;scale by true baseline
length so translation direction and all original free parameter blocks match.
Forward replay against clean raw training pixels must agree<=1e-8px.

Reuse the existing read-only central-difference Jacobian plus half-step witness,
without applying ANY step. Expose that existing linearization to avoid a duplicate
camera parameterization;old audit outputs must replay. Profile the focal column
against all nuisance columns with column-normalized SVD least-squares,rcond1e-12.
Full-rank focal contrast needs rank(augmented)=rank(nuisance)+1;otherwise report
unidentified,not a finite pseudo-inverse confidence. For identifiable contrast,
local sigma(logf)=.5/||J_f-proj_nuisance(J_f)||. Validate the math on a public
closed-form identified case and a truly confounded focal/nuisance case;also
check nuisance scaling/permutation invariance. Preserve singular values/ranks.

This is a local Gaussian,independent-equal-variance,unbiased-regular-model Fisher
diagnostic at procedural truth,not global identifiability,an achieved error,
patient confidence interval or medical millimeters. Approximate sigma(logf)
is relative focal uncertainty only to first order. Report1.96sigma illustratively,
not a calibrated finite-sample guarantee. If sigma(logf)>=.02or unidentified,
prioritize genuinely additional information rather than another optimizer on
this fixture. If smaller,it only motivates further optimizer diagnosis,not proof
of a particular bug or permission to rescue0308cached predictions.

No real video/scan/bone/case002pixel,no new noise/model/seed/focal/solver fit,
download/training/upload. No actual3px/2mm/visual gate or production default
change. Implementation<=600s,worker<=120s/1GiB,whole1200sfrom registration,
including tests/evidence and local commit. CPUmath environment4threads. Keep
verified generic linearization/information math and one regression;retire the
one-off controller after compact source/evidence/protection checks. Stop on
invalid replay/rank/witness rather than threshold search. No head is produced.

## Actual result:additional information first,not a solver-rescue inference

Executed source7415597;one read-only worker starts09:21:55.012Z,0.360sinside
(parent1.688s),conservative observed tree peak125456384bytes. Public closed-form
identified/confounded/scaling/permutation checks pass. Old/new audit dictionaries
on the original public8point fixture agree in every field,including array bytes.
No step,fit,human input or model call occurs. Exact truth/native/gauge replay
max4.55e-13px. Local focal contrast is identifiable,but sigma(logf)=.0760183
under sigma.5pxindependent coordinate noise;illustrative1.96sigma=.148996.

Decision per preregistration:ADDITIONAL_INFORMATION_FIRST. In THIS procedural
geometry/noise/fold,the local unbiased-regular Gaussian information is weak
relative to the2%focal target.0310's8.46%error is not by itself evidence of a
specific solver bug. A different biased estimator/geometry/prior could behave
differently,and the information calculation is not a global or patient error
lower bound. Nonconvergence remains real but additional iterations/another
solver on this fixture is not justified by a belief that precise focal is
already determined by the data. Do not declare3px/2mmor physical camera passed.

Retain successful generic read-only linearization/profile-information math and
one public regression;no production camera implementation/default changed.
The two intentional source/test changes relative to earlier protection ledgers
must be explicitly amended without replacing old hashes. Active one-off driver
is retired after compact raw Jacobian/ranks/replay/source/worker evidence.
