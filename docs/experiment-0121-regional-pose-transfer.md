# Experiment 0121: physical rotation transfer across facial regions

Use experiment 0120's eleven frontal-ray candidate correspondences and current
camera matrices. Fit only the four eye and two nose depths plus two oblique
rotation vectors. Intrinsics, camera centers, frontal/profile cameras and
input observations stay fixed. Rotation components are bounded +/-0.02 rad,
with 0.02 rad prior and 3 px observation scale. All fitted depths are positive.

Freeze the resulting cameras before refitting the four mouth depths and one
chin depth. Those five points do not train the camera correction. Their image
observations were used in prior development, so exclusion from this solve is
not independent acceptance. This is a free-point camera hypothesis, not a new
head model. Detector and chin-contour correspondence uncertainties remain.

| Region | Before left/right mean error px | After left/right mean error px |
| --- | --- | --- |
| Eyes (fit) | 3.5987 / 3.0077 | 4.8595 / 3.8460 |
| Nose (fit) | 12.7836 / 7.4466 | 7.4131 / 3.9473 |
| Mouth (excluded from camera fit) | 7.8236 / 4.7786 | 1.9213 / 1.0907 |
| Chin (excluded from camera fit) | 3.3359 / 2.4391 | 9.7060 / 6.8398 |

The solve converges with no active bound. Rotation vectors are
[0.0029056,-0.0149409,-0.0088378] and
[0.0028699,0.0139473,0.0096307] radians. Positive depth is verified for all
points in all five cameras. The regional depth solutions shift substantially;
the free-point improvement cannot be applied to an unchanged head by assumption.

Unlike a uniform image translation, this physical rotation hypothesis transfers
strongly to the excluded mouth. However, eye and chin regressions prevent
camera promotion: `REJECT`. Do not discard the contradictory region or enlarge
bounds just to promote the central-face result. Chin silhouette localization
may not denote one physical 3D point, but that possibility requires evidence,
not silent exclusion. No actual-head improvement is claimed and no new render
is needed to reject this diagnostic candidate before promotion.

Private `regional-pose-transfer-v1` preserves camera matrices, before/after
depths, group errors and bounds. The source regional report SHA-256 is
`d41077fd52276783152188e69f0ec0d662eaa0e0e9ab360646887e8e185b392e`.
All private data remain local. The existing camera gate is unchanged.

Next discriminate correspondence semantics from pose using reviewed eye and
chin supports on the actual surface. Treat apparent chin outline as a curve
constraint when appropriate, not automatically as one fixed material point.
Any coupled head trial must protect eye alignment and evaluate the full face.
