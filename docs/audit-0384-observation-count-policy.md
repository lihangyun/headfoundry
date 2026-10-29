# 0384: observation-count policy audit, not a reconstruction replay

2026-10-29. Read-only arithmetic on0383archived queried observations. No model,
camera fit, image re-extraction, held-point selection or production change.
Original0383REJECT remains. Archive SHA verified:
75559d3b50277fddc66b6a50f179d1bb4633e885976fb905dee864c060b62266.
Raw observation member SHA:
c9d28a59acbd23eefb68542fca71d4d6a47e18af9fdb217435e31030a130757b.

## What actually blocked the previous run

0332/0333 carried >=48complete, floor20%held with >=9held and >=36train.
0352 already explicitly described48as operational, not a mathematical minimum.
0383 copied this policy without independent evidence that it discriminates
physical accuracy for the new dense-lattice observations. At37, floor20%=7
would also miss the separate9held policy; simply changing48alone would not
complete the registered protocol. No retrospective split or solve was run here.

This is a research-design weakness: a conservative count gate was again made
the terminal decision before measuring the actual geometric capability. It must
not be reported as a measured model-accuracy failure. Nor should arbitrary
dense sampling inflate a count to make the same information look sufficient.

## Verified raw evidence

All37admitted coordinates are unique in each view. Pairwise minimum separation
is24.000/13.287/18.432nativepx; spans216x240,173.447x244.555,213.830x216.604px.
Centered2Dsingular values are(510.257,356.706),(514.664,285.648),
(464.800,349.292): not duplicate/collinear image sets. These are descriptive
statistics, NOT proof of material identity, rigidity, independent noise,
parallax, 3Dnonplanarity or full camera-Jacobian rank.

With a hypothetical fixed9whole-point holdout,28training points remain.
Existing anchored/unit-baseline three-view parameterization has12camera scalars
(commonf1 + secondpose5 + thirdpose6) plus3perpoint:96unknowns against168scalar
image observations. Thus simple equation counting does not rule it out. This
is a necessary dimensional check only, not a sufficient identifiability proof
or a prediction that the previous initializer will work. No solve was made.

## Decision and authority boundary

Do not download any weights again. Preserve raw108including all37candidates.
An informative next test would consume these exact saved observations, freeze
9held/28train by the original deterministic hash order before scoring, and run
one unchanged camera solve with full seed/depth/rank/held evidence. Actual3px,
2mm, mesh and visual gates stay unchanged; even consistency pass is partial.

However this changes0383's explicit count/split stop rule after observing its
result. It requires an explicit exception, not a quiet claim of a new algorithm.
Request one archive-only geometry test (<=20minutes total; one180s/2GiBsolve;
no additional NN call, filtering, seed/threshold/frame sweep). If approved,
register separately before executing; if not, do not run it. Future proposals
should justify sample-policy sensitivity prospectively, not repeat hard-count
stops followed by expensive model reinstalls. No shared gate is edited here.
