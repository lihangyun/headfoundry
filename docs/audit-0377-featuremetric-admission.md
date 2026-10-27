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
