# 0377: featuremetric refinement admission screen

2026-10-28. Public-source review only; no installation, model inference, training,
camera fitting or head generation. Existing goal remains active.

## Candidate contribution, not an end-to-end replacement

Pixel-Perfect SfM adjusts matched 2D keypoints jointly before geometric estimation,
then refines cameras/points using dense learned features. This is potentially
different from the pairwise DIS admission failure in0333: it targets localization
of an existing track jointly, rather than independently propagating each pair.
It is NOT evidence that missing physical correspondences can be recovered.

Reviewed primary sources:
- https://arxiv.org/abs/2108.08291 (abstract, not full-paper verification)
- https://raw.githubusercontent.com/cvg/pixel-perfect-sfm/main/README.md
- https://raw.githubusercontent.com/cvg/pixel-perfect-sfm/main/LICENSE
- https://raw.githubusercontent.com/cvg/pixel-perfect-sfm/main/doc/features.md

Repository license is Apache-2.0. This does not establish rights for all default
feature weights or transitive dependencies. README names S2DNet as default and
requires supplied keypoints/matches. It lists a source-built COLMAP/Ceres stack
and says Windows is untested. No dependency stack is approved or installed here.

## Decision

UNVERIFIED as a HeadFoundry component. Do not launch an end-to-end installation
on the assumption that this supplies the missing cross-axis identities. Its
supported role is candidate localization refinement, not an identity oracle.
Low feature loss, cycle closure and low training reprojection cannot certify
that two observations belong to the same physical point.

Next admission work is bounded to one source/protocol review (30 minutes):
inspect the actual optimization domain and displacement restrictions, exact
feature-weight rights, and whether existing saved case001 observations provide
independently supportable seeds. Do not reinstall a rejected extractor to create
those seeds. If the seed prerequisite is absent, stop this candidate at admission;
record that as a missing prerequisite, not measured model inaccuracy.

Only after admission can an executable experiment be registered: freeze input
observations and whole-point holdout, compare unchanged observations with joint
refinement, keep cameras/backend fixed between arms, preserve all rejected
observations and report coverage as well as error. Any learned-feature baseline
must be separated from the effect of joint refinement. No retrospective point
selection or threshold sweep. Actual3px/2mm/visual acceptance remains unchanged.

This review narrows a possible component role; it is not a reconstruction gain.

## Completed mechanism review

Read paper sections4.1-4.4 (not just abstract):
https://arxiv.org/html/2108.08291v1
and implementation entry:
https://raw.githubusercontent.com/cvg/pixel-perfect-sfm/main/pixsfm/keypoint_adjustment/main.py

Important correction to the admission wording above: tentative matches need not
already be independently certified physical identities. The method deliberately
refines them before geometric verification. Demanding certified correspondences
before any refinement would rule out its actual intended use without testing it.
Independent evidence is required for claiming accuracy, not for admitting a
bounded experiment with uncertain inputs.

It separates conflicting track assignments, optimizes within supplied tentative
tracks, and fixes a reference observation to prevent drift. The paper bounds
movement to8pixels; the current Python configuration contains bound4.0. These
are distinct source settings, not interchangeable claims about a tested setup.
Dense local descriptors are explicitly not a global identity disambiguator.
The paper also permits normalized local intensity patches instead of a network.
That is a possible independent, dependency-light implementation, not equivalent
evidence for S2DNet's learned illumination/viewpoint invariance.

S2DNet-Minimal's loader repository has MIT license:
https://raw.githubusercontent.com/germain-hug/S2DNet-Minimal/master/LICENSE
Its README links externally hosted weights without an explicit weight-specific
license statement. This review has not established that those external bytes
are covered. Default learned integration remains unapproved; no download made.

## Existing inputs and next-action decision

0257's five manual candidate groups are not a distributed measurement set.
However0344/0352 preserve22 complete tentative tracks across three actual frames
and a fixed13train/9held split. Their initializer failure does not establish that
every track is wrong. This is a concrete existing input, not a need to reinstall
ALIKED or manufacture scan-derived correspondences. Reviewed the actual0344,
0352 and0257 protocols/results here; raw arrays were not re-scored in this review.

Next candidate is an independent **root-fixed, joint local patch refinement** of
those saved tentative observations, compared to unchanged observations. It must
first register actual input hashes, fixed movement/patch limits, controls and
whole-point holdout. This is a different observation objective, not a seed,
focal-bound or acceptance-threshold change to rescue0352. No execution is
authorized by this document alone; its bounded experiment must specify how it
handles invalid/ambiguous patches without cherry-picking, and preserve the
unchanged baseline failure as a failure.

The13/9 population can support a limited diagnostic, not automatic production
entry or a relaxation of the historical48-track policy. No formal head fit may
follow merely because this small-population test succeeds. If its identity or
precision remains unresolved, report UNVERIFIED rather than certifying matches
from patch cost. Pose, all held observations and negative controls must be
reported separately. No actual3D or medical accuracy has been measured here.

Closeout: no runtime/weights/outputs were created, so no failed integration needs
deletion. The next action changes from installing pixsfm or rejecting all seeds
to preregistering the minimal image-evidence experiment. Goal remains active.
